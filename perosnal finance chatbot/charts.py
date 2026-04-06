
import matplotlib.pyplot as plt
from database import fetch_all

def show_bar_chart():
    data = fetch_all()
    if not data:
        print("No expenses to show.")
        return

    # Aggregate amounts by category
    category_totals = {}
    for _, amount, category, *_ in data:
        category_totals[category] = category_totals.get(category, 0) + amount

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    plt.figure(figsize=(8,5))
    plt.bar(categories, amounts, color='skyblue')
    plt.title("Expenses by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount")
    plt.show()
