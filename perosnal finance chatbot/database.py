import sqlite3

DB_FILE = "finance.db"

def insert_expense(amount, category, note, timestamp):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO expenses (amount, category, note, timestamp) VALUES (?, ?, ?, ?)",
                (amount, category, note, timestamp))
    conn.commit()
    conn.close()

def fetch_last(n):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, amount, category, note, timestamp FROM expenses ORDER BY timestamp DESC LIMIT ?", (n,))
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_by_id(expense_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()

def fetch_all():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, amount, category, note, timestamp FROM expenses ORDER BY timestamp DESC")
    rows = cur.fetchall()
    conn.close()
    return rows
