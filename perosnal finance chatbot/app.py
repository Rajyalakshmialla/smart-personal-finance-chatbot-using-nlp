from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime, timedelta
import sqlite3
import json
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from nlp_model import get_intent
from database import insert_expense, fetch_all, delete_by_id, fetch_last
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DB_FILE = 'finance.db'

# ==================== Database Helper ====================
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== User/Auth Setup ====================
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL
        )
    ''')
    cur.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    if cur.fetchone() is None:
        cur.execute(
            'INSERT INTO users (username, password_hash, full_name) VALUES (?, ?, ?)',
            ('admin', generate_password_hash('admin123'), 'Finance Admin')
        )
    conn.commit()
    conn.close()

init_db()

# ==================== API Routes ====================
@app.route('/')
def index():
    return render_template('index.html', user=session.get('user'))

@app.before_request
def require_login():
    if request.endpoint in ('login', 'register', 'static', 'favicon'):
        return
    if 'user' not in session:
        if request.path.startswith('/api'):
            return jsonify({'error': 'Login required'}), 401
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT username, password_hash, full_name FROM users WHERE username = ?', (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user'] = {'username': user['username'], 'full_name': user['full_name']}
            session.permanent = True
            return redirect(url_for('index'))

        flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip() or username

        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('register.html')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cur.fetchone():
            conn.close()
            flash('Username already exists', 'danger')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        cur.execute(
            'INSERT INTO users (username, password_hash, full_name) VALUES (?, ?, ?)',
            (username, password_hash, full_name)
        )
        conn.commit()
        conn.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('budget', None)
    return redirect(url_for('login'))

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall financial statistics"""
    data = fetch_all()
    if not data:
        return jsonify({
            'total_spent': 0,
            'transaction_count': 0,
            'average_transaction': 0,
            'top_category': 'N/A',
            'this_month': 0
        })
    
    total_spent = sum([d[1] for d in data])
    transaction_count = len(data)
    average = total_spent / transaction_count if transaction_count > 0 else 0
    
    # Get top category
    categories = {}
    for d in data:
        cat = d[2]
        categories[cat] = categories.get(cat, 0) + d[1]
    top_category = max(categories, key=categories.get) if categories else "N/A"
    
    # Get this month's spending
    today = datetime.now()
    month_start = datetime(today.year, today.month, 1)
    this_month = sum([d[1] for d in data if datetime.strptime(d[4], "%Y-%m-%d %H:%M:%S") >= month_start])
    
    return jsonify({
        'total_spent': round(total_spent, 2),
        'transaction_count': transaction_count,
        'average_transaction': round(average, 2),
        'top_category': top_category,
        'this_month': round(this_month, 2)
    })

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    """Get all expenses with filters"""
    data = fetch_all()
    expenses = []
    for d in data:
        expenses.append({
            'id': d[0],
            'amount': d[1],
            'category': d[2],
            'description': d[3],
            'date': d[4]
        })
    return jsonify(expenses)

@app.route('/api/expenses/category', methods=['GET'])
def get_category_breakdown():
    """Get spending by category"""
    data = fetch_all()
    categories = {}
    for d in data:
        cat = d[2]
        categories[cat] = categories.get(cat, 0) + d[1]
    return jsonify(categories)

@app.route('/api/expenses/timeline', methods=['GET'])
def get_timeline():
    """Get spending over time (daily)"""
    data = fetch_all()
    timeline = {}
    for d in data:
        date = d[4].split()[0]
        timeline[date] = timeline.get(date, 0) + d[1]
    
    sorted_dates = sorted(timeline.items())
    return jsonify({
        'dates': [item[0] for item in sorted_dates],
        'amounts': [item[1] for item in sorted_dates]
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process user message and return response"""
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    intent = get_intent(user_message)
    response = process_chat_intent(intent, user_message)
    
    return jsonify({
        'intent': intent,
        'response': response,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/add-expense', methods=['POST'])
def add_expense():
    """Add a new expense"""
    data = request.json
    amount = data.get('amount')
    category = data.get('category', 'General')
    description = data.get('description', '')
    date_input = data.get('date', '')
    
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount'}), 400

    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400

    if date_input:
        try:
            date_input = date_input.replace('T', ' ')
            if len(date_input) == 16:
                date_input = f"{date_input}:00"
            date = datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    else:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    insert_expense(amount, category, description or f"{category} expense", date)

    over_budget_message = None
    budget_amount = session.get('budget')
    if budget_amount is not None:
        data = fetch_all()
        today = datetime.now()
        month_start = datetime(today.year, today.month, 1)
        this_month_spent = sum([d[1] for d in data if datetime.strptime(d[4], "%Y-%m-%d %H:%M:%S") >= month_start])
        if this_month_spent > budget_amount:
            over_amount = this_month_spent - budget_amount
            over_budget_message = f"⚠️ You've exceeded this month's budget by ₹{round(over_amount, 2)}. Try to reduce spending for the rest of the month."

    response = {
        'success': True,
        'message': f'Added ₹{amount} to {category}'
    }
    if over_budget_message:
        response['warning'] = over_budget_message

    return jsonify(response)

@app.route('/api/delete-expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense"""
    delete_by_id(expense_id)
    return jsonify({'success': True, 'message': 'Expense deleted'})

@app.route('/api/budget', methods=['GET', 'POST'])
def budget():
    """Get or set budget"""
    if request.method == 'POST':
        data = request.json
        session['budget'] = data.get('budget')
        return jsonify({'success': True})
    
    budget_amount = session.get('budget', 5000)
    data = fetch_all()
    today = datetime.now()
    month_start = datetime(today.year, today.month, 1)
    this_month_spent = sum([d[1] for d in data if datetime.strptime(d[4], "%Y-%m-%d %H:%M:%S") >= month_start])
    remaining = budget_amount - this_month_spent
    
    return jsonify({
        'budget': budget_amount,
        'spent': round(this_month_spent, 2),
        'remaining': round(remaining, 2),
        'percentage': min(100, round((this_month_spent / budget_amount * 100), 1)) if budget_amount > 0 else 0,
        'over_budget': this_month_spent > budget_amount,
        'over_amount': round(max(0, this_month_spent - budget_amount), 2)
    })

@app.route('/api/insights', methods=['GET'])
def get_insights():
    """Get AI-powered financial insights"""
    data = fetch_all()
    if not data:
        return jsonify([])
    
    insights = []
    total = sum([d[1] for d in data])
    
    # Analyze spending patterns
    categories = {}
    for d in data:
        cat = d[2]
        categories[cat] = categories.get(cat, 0) + d[1]
    
    # Top category insight
    if categories:
        top_cat = max(categories, key=categories.get)
        top_amount = categories[top_cat]
        percentage = (top_amount / total * 100) if total > 0 else 0
        insights.append(f"💡 Your top category is **{top_cat}** with ₹{round(top_amount, 2)} ({round(percentage, 1)}%)")
    
    # Average daily spending
    if len(data) > 1:
        first_date = datetime.strptime(data[0][4], "%Y-%m-%d %H:%M:%S")
        last_date = datetime.strptime(data[-1][4], "%Y-%m-%d %H:%M:%S")
        days = (last_date - first_date).days + 1
        daily_avg = total / days if days > 0 else 0
        insights.append(f"📊 Your average daily spending is ₹{round(daily_avg, 2)}")
    
    # This month trend
    today = datetime.now()
    month_start = datetime(today.year, today.month, 1)
    this_month = sum([d[1] for d in data if datetime.strptime(d[4], "%Y-%m-%d %H:%M:%S") >= month_start])
    insights.append(f"📈 This month's spending: ₹{round(this_month, 2)}")

    budget_amount = session.get('budget')
    if budget_amount is not None:
        if this_month > budget_amount:
            over_amount = round(this_month - budget_amount, 2)
            insights.append(f"⚠️ You are over your monthly budget by ₹{over_amount}. Try to cut spending this month or raise your budget next month.")
        else:
            saving = round(budget_amount - this_month, 2)
            insights.append(f"✅ You are within budget. You can still spend ₹{saving} this month.")
    
    return jsonify(insights)

@app.route('/api/export', methods=['GET'])
def export_data():
    """Export expenses as CSV"""
    import csv
    from io import StringIO
    
    data = fetch_all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Amount', 'Category', 'Description', 'Date'])
    
    for d in data:
        writer.writerow([d[0], d[1], d[2], d[3], d[4]])
    
    response = app.response_class(
        response=output.getvalue(),
        status=200,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=expenses.csv"}
    )
    return response

# ==================== Chat Intent Processing ====================
def process_chat_intent(intent, query):
    """Process different intents and generate responses"""
    
    if intent == "add_expense":
        words = query.split()
        amount = None
        category = "General"
        
        for w in words:
            try:
                amount = float(w.replace('₹', '').replace('$', ''))
            except ValueError:
                continue
        
        categories = ["food", "rent", "transport", "shopping", "entertainment", "utilities", "health", "entertainment"]
        for c in categories:
            if c in query.lower():
                category = c.capitalize()
        
        if amount is None:
            return "❌ I couldn't detect the amount. Try: 'Add 50 for lunch' or use the expense form."
        
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_expense(amount, category, query, date)
        return f"✅ Perfect! I've added **₹{amount}** to **{category}**. Keep tracking! 💪"
    
    elif intent == "show_balance":
        data = fetch_all()
        if not data:
            return "📭 No expenses yet. Start tracking by adding your first expense!"
        total = sum([d[1] for d in data])
        return f"💰 **Total Spent**: ₹{round(total, 2)}\n\nYou have {len(data)} expense(s). Want to see breakdown by category?"
    
    elif intent == "show_expense":
        data = fetch_all()
        if not data:
            return "📭 No expenses found yet."
        response = "📝 **Your Recent Expenses**:\n\n"
        total = 0
        for d in list(data)[-10:]:  # Last 10
            response += f"• ₹{d[1]} - {d[2]} ({d[4][:10]})\n"
            total += d[1]
        response += f"\n**Total**: ₹{round(total, 2)}"
        return response
    
    elif intent == "show_chart":
        return "📈 Opening charts... Check the Dashboard tab for visualizations!"
    
    elif intent == "delete_expense":
        last = fetch_last(1)
        if last:
            delete_by_id(last[0][0])
            return f"🗑️ Deleted: ₹{last[0][1]} - {last[0][2]}"
        return "❌ No expenses to delete."
    
    elif intent == "set_reminder":
        return "⏰ Reminders coming soon! Use our calendar integration for now."
    
    else:
        return "🤔 I can help with:\n- Adding expenses\n- Checking balance\n- Viewing breakdown\n- Setting budgets\n- Getting insights\n\nWhat would you like to do?"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
