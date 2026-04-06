# smart-personal-finance-chatbot-using-nlp
# 💰 Personal Finance Manager Pro

A professional, full-featured personal finance management application with AI-powered chat assistance.

## 🌟 Features

### Dashboard
- **Real-time Statistics**: Total spent, transaction count, average transaction, monthly spending
- **Visual Charts**: Spending trends and category breakdown with Chart.js
- **Financial Insights**: AI-powered analysis and spending patterns
- **Budget Tracking**: Set and monitor your monthly budget with visual progress indicators

### Expense Management
- **Add Expenses**: Quick form to record spending with categories
- **View All Expenses**: Searchable expense table with filters
- **Delete Expenses**: Remove unwanted entries
- **Export Data**: Download all expenses as CSV

### Analytics
- **Category Breakdown**: Pie and bar charts by spending category
- **Spending Trends**: Daily spending visualization over time
- **Monthly Reports**: See month-to-date spending analysis
- **Spending Patterns**: Identify your top categories and average daily spend

### AI Chat Assistant
- **Natural Language Processing**: Ask questions in natural language
- **Smart Intent Recognition**: Understands "add 50 for lunch" or "show my balance"
- **Financial Advice**: Get insights and recommendations
- **Automated Responses**: Instant feedback on your requests

### Budget Management
- **Budget Setting**: Define your monthly or weekly budget
- **Progress Tracking**: Visual progress bar showing budget status
- **Spending Alerts**: Warnings when you exceed budget
- **Remaining Balance**: Know how much you can still spend

## 🏗️ Project Structure

```
personal-finance-chatbot/
├── app.py                    # Flask backend application
├── templates/
│   └── index.html           # Main HTML interface
├── static/
│   ├── style.css            # Professional styling
│   └── script.js            # Frontend interactivity
├── database.py              # Database operations
├── nlp_model.py             # Intent recognition
├── charts.py                # Chart generation
├── reminders.py             # Reminder functionality
├── finance.db               # SQLite database
└── requirements.txt         # Python dependencies
```

## 🚀 Getting Started

### Installation

1. **Activate Virtual Environment**:
```bash
.venv\Scripts\Activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
python app.py
```

The application will be available at: **http://localhost:5000**

## 💡 How to Use

### Adding Expenses
1. Click **"Add Expense"** in the sidebar
2. Enter amount, category, and description
3. Click **"Add Expense"** to save

Or use **AI Chat**: "Add 50 for lunch"

### Checking Statistics
- **Dashboard**: See all-time stats
- **AI Chat**: "How much have I spent?" or "Show my balance"

### Setting Budget
1. Go to **Budget** tab
2. Enter your monthly budget amount
3. Click **"Set Budget"**
4. Monitor progress with the visual indicator

### Viewing Analytics
- Click **Analytics** to see detailed charts
- Check **Dashboard** for quick insights
- Export data for external analysis

### Using AI Chat
- Type naturally: "Add 100 for groceries"
- Ask questions: "Show my expenses"  
- Get insights: "What's my top category?"
- Set reminders: "Remind me tomorrow"

## 📊 API Endpoints

### Statistics
- `GET /api/stats` - Get overall financial statistics
- `GET /api/insights` - Get AI-powered financial insights

### Expenses
- `GET /api/expenses` - Get all expenses
- `GET /api/expenses/category` - Get spending by category
- `GET /api/expenses/timeline` - Get daily spending trend
- `POST /api/add-expense` - Add new expense
- `DELETE /api/delete-expense/<id>` - Delete an expense

### Budget
- `GET /api/budget` - Get budget information
- `POST /api/budget` - Set monthly budget

### Chat
- `POST /api/chat` - Process user message with AI

### Export
- `GET /api/export` - Export expenses as CSV

## 🎨 Design Features

- **Modern UI**: Clean, professional interface with glassmorphism
- **Responsive Design**: Works on desktop and tablet
- **Dark Sidebar**: Easy navigation
- **Gradient Accents**: Visual hierarchy with primary and secondary colors
- **Smooth Animations**: Fade-ins and hover effects
- **Chart Visualizations**: Chart.js for interactive graphs

## 🔧 Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite
- **Charts**: Chart.js
- **Icons**: Font Awesome
- **Processing**: NLP for intent recognition

## 📈 Performance Features

- **Real-time Updates**: Data refreshes automatically
- **Efficient Database**: Optimized queries
- **Fast API Responses**: JSON endpoints
- **Client-side Rendering**: Smooth user experience
- **Progressive Loading**: Data loads on demand

## 🔐 Security

- Session-based authentication (ready for expansion)
- CSRF protection ready
- Input validation
- Secure database operations

## 🎯 Future Enhancements

- User authentication and multi-user support
- Cloud sync for expenses
- Mobile app
- Recurring expenses
- Savings goals
- Investment tracking
- Integration with bank APIs

## 📝 License

Personal Finance Manager Pro - All Rights Reserved

---
