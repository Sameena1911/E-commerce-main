from flask import Flask, render_template, jsonify, request
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from sqlalchemy import func
import io 
from datetime import datetime, timedelta
from io import BytesIO
import base64
from . import db
from . models import *
from flask import Blueprint
visualization = Blueprint('visualization',__name__,static_folder='static')


@visualization.route('/')
def home():
    # Render the home page without any chart data
    return render_template('visualization.html', chart_url=None)
@visualization.route('/roles_chart')
def roles_chart():
    # Fetch user data for visualization
    roles = db.session.query(User.role, db.func.count(User.role)).group_by(User.role).all()
    roles_dict = {role: count for role, count in roles}

    # Generate Pie Chart
    labels = roles_dict.keys()
    sizes = roles_dict.values()
    colors = ['#A3D8F4', '#FFCF9F', '#B8F0D3', '#F9D5E5', '#FFE4C4']  # Subtle colors
    explode = [0.1 if max(sizes) == size else 0 for size in sizes]  # Highlight the largest segment

    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

    # Save the chart to a PNG image
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    pie_chart_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    # Analytics Data
    total_users = sum(sizes)
    analytics_data = {
        "total_users": total_users,
        "role_distribution": roles_dict
    }

    return render_template('roles.html', pie_chart_url=pie_chart_url, analytics_data=analytics_data,title='Roles Chart',side_title='Real Time data',t1='Total Users:',t2='Role breakdown')


@visualization.route('/sales_by_city')
def sales_by_city():
    # Query database to group users by city and calculate sales (mock data below)
    city_sales = db.session.query(User.city, db.func.count(User.id)).group_by(User.city).all()

    # Data preparation for visualization
    cities = [item[0] for item in city_sales]
    sales = [item[1] * 100 for item in city_sales]  # Assuming each user contributes $100 to sales

    # Create bar chart with three basic colors
    fig = Figure()
    ax = fig.subplots()
    colors = ['#FF9999', '#99CCFF', '#FFCC99']  # Three basic colors (light red, blue, and orange)
    ax.bar(cities, sales, color=colors[:len(cities)])
    ax.set_title('Sales by City', fontsize=16)
    ax.set_xlabel('City', fontsize=12)
    ax.set_ylabel('Sales ($)', fontsize=12)
    ax.set_xticklabels(cities, rotation=45, ha='right')

    # Save chart to BytesIO object
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()

    # Pass chart URL and data to the template
    return render_template('sales_city.html', chart_url=chart_url, city_sales=city_sales,title='sales by city',side_title='Real Time data',t1='City',t2='Sales')

@visualization.route('/revenue_trends')
def revenue_trends():
    # Dummy data for revenue trends
    categories = ["Electronics", "Fashion", "Groceries", "Books", "Home Appliances"]
    revenues = [500000, 300000, 200000, 100000, 150000]  # In INR
    total_orders = 3000  # Total number of orders (dummy value)
    previous_year_revenue = 1000000  # INR (2024)
    current_year_revenue = sum(revenues)  # INR (2025)

    # Calculate expected revenue for 2030 based on a growth rate
    growth_rate = 0.1  # Assume 10% growth rate annually
    years = 2030 - 2025
    expected_revenue_2030 = current_year_revenue * ((1 + growth_rate) ** years)

    # Analytics data
    # Analytics data
    analytics = {
    "Total Orders": f"{total_orders}",
    "Total Revenue (INR)": f"{current_year_revenue:,}",
    "Expected Revenue in 2030 (INR)": f"{expected_revenue_2030:,.2f}",
    "Previous Year Revenue (INR)": f"{previous_year_revenue:,}",
    "Current Year Revenue (INR)": f"{current_year_revenue:,}",
    "Top Category": categories[revenues.index(max(revenues))],
    "Least Category": categories[revenues.index(min(revenues))],
    "Categories": list(zip(categories, revenues))  # Add categories and revenue as tuples
    }


    # Create a pie chart
    plt.figure(figsize=(8, 6))
    colors = ['#A2D2FF', '#BDE0FE', '#FFAFCC', '#FFC8DD', '#D4A5A5']
    plt.pie(
        revenues,
        labels=categories,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        textprops={'color': '#333', 'fontsize': 12}
    )
    plt.title("Revenue by Category (INR)", fontsize=16, color="#264653")

    # Save chart as base64 string
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    plt.close()

    return render_template(
        "revenue_trends.html",
        chart_data=chart_data,
        analytics=analytics,
        previous_year_revenue=previous_year_revenue,
        current_year_revenue=current_year_revenue
    )
@visualization.route('/delivery_chart')
def delivery_chart():
    # Example data (replace with database query)
    order_status_counts = {
        "Pending": 15,
        "Shipped": 25,
        "Delivered": 50,
        "Failed": 10
    }

    # Data for stacked bar chart
    categories = ["Pending", "Shipped", "Delivered", "Failed"]
    values = list(order_status_counts.values())
    
    # Subtle pastel colors
    colors = ['#f4a261', '#a8dadc', '#2a9d8f', '#e76f51']  # Light orange, light teal, green, soft red

    # Create a horizontal stacked bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(categories, values, color=colors)
    ax.set_xlabel("Number of Orders", fontsize=12)
    ax.set_title("Order Status Distribution", fontsize=16)
    ax.grid(alpha=0.3)

    # Save chart as a base64 string
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()

    # Analytics Data
    total_orders = sum(values)
    analytics = {
        "Pending Orders": order_status_counts["Pending"],
        "Shipped Orders": order_status_counts["Shipped"],
        "Delivered Orders": order_status_counts["Delivered"],
        "Failed Orders": order_status_counts["Failed"],
        "Total Orders": total_orders,
    }

    # Sample order table data
    orders = [
        {"id": 1, "amount": 200, "status": "Pending", "payment": "Cash on Delivery"},
        {"id": 2, "amount": 350, "status": "Delivered", "payment": "Credit Card"},
        {"id": 3, "amount": 150, "status": "Failed", "payment": "UPI"},
        {"id": 4, "amount": 400, "status": "Shipped", "payment": "Cash on Delivery"},
        {"id": 5, "amount": 250, "status": "Delivered", "payment": "UPI"},
    ]

    return render_template(
        "delivery_chart.html", chart_data=chart_data, analytics=analytics, orders=orders
    )
@visualization.route("/customer_trends")
def customer_trends():
    # Data for the chart
    today = datetime.today()
    days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(12)]  # Adjust for 12 days
    new_customers = [100, 120, 140, 130, 150, 180, 200, 220, 240, 260, 280, 300]
    returning_customers = [50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 220]

    # Ensure days, new_customers, and returning_customers all have the same length
    if len(days) != len(new_customers) or len(days) != len(returning_customers):
        raise ValueError("Data dimensions do not match. Ensure all lists have the same length.")

    # Generate the chart using Matplotlib
    plt.figure(figsize=(10, 5))
    bar_width = 0.4
    x_indices = range(len(days))

    plt.bar(x_indices, new_customers, width=bar_width, label="New Customers", color="#6a89cc", alpha=0.8)
    plt.bar([x + bar_width for x in x_indices], returning_customers, width=bar_width, label="Returning Customers", color="#82ccdd", alpha=0.8)

    plt.title("New and Returning Customers Trends", fontsize=14)
    plt.xlabel("Days")
    plt.ylabel("Number of Customers")
    plt.xticks([x + bar_width / 2 for x in x_indices], days, rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()

    # Save the chart to a buffer and encode it as a base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    # Example data for the table
    new_customers_details = [
        {"name": "John Doe", "location": "New York", "date_joined": datetime(2025, 1, 1)},
        {"name": "Jane Smith", "location": "Los Angeles", "date_joined": datetime(2025, 1, 5)},
        {"name": "Michael Johnson", "location": "Chicago", "date_joined": datetime(2025, 1, 7)},
        {"name": "Alice Williams", "location": "San Francisco", "date_joined": datetime(2025, 1, 10)},
        {"name": "David Brown", "location": "Houston", "date_joined": datetime(2025, 1, 12)},
    ]

    # Total counts
    total_new_customers = sum(new_customers)
    total_returning_customers = sum(returning_customers)

    return render_template(
        "Customer_trends.html",
        chart_base64=chart_base64,
        new_customers_details=new_customers_details,
        total_new_customers=total_new_customers,
        total_returning_customers=total_returning_customers,
    )

@visualization.route("/financial_health")
def financial_health():
    # Generate random daily data for financial performance
    today = datetime.today()
    days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]
    revenue = [1000, 1500, 2000, 2500, 3000]
    expenses = [800, 1200, 1500, 2000, 2500]
    profit = [revenue[i] - expenses[i] for i in range(len(revenue))]

    financial_data = [
        {"customer": "ab", "product": "Laptop", "quantity": 2, "total": 2000, "expenses": 1500, "profit": 500},
        {"customer": "Bb", "product": "Smartphone", "quantity": 3, "total": 3000, "expenses": 2200, "profit": 800},
        {"customer": "Cc", "product": "Headphones", "quantity": 5, "total": 500, "expenses": 300, "profit": 200},
        {"customer": "Dd", "product": "Monitor", "quantity": 1, "total": 300, "expenses": 200, "profit": 100},
        {"customer": "Ee", "product": "Keyboard", "quantity": 4, "total": 400, "expenses": 300, "profit": 100},
    ]

    # Generate real-time analytics data for the right side panel
    real_time_analytics = {
        "Current Revenue": f"{revenue[-1]}",
        "Current Expenses": f"{expenses[-1]}",
        "Current Profit": f"{profit[-1]}",
    }

    # Generate line chart with subtle colors
    plt.figure(figsize=(10, 5))
    pastel_colors = {
        "Revenue": "#a8dadc",  # Light blue-green
        "Expenses": "#f4a261",  # Light orange
        "Profit": "#e76f51"    # Soft red
    }
    plt.plot(days, revenue, marker='o', label="Revenue", color=pastel_colors["Revenue"], linewidth=2)
    plt.plot(days, expenses, marker='o', label="Expenses", color=pastel_colors["Expenses"], linewidth=2)
    plt.plot(days, profit, marker='o', label="Profit", color=pastel_colors["Profit"], linewidth=2)
    plt.title("Financial Performance Over Time", fontsize=16)
    plt.xlabel("Days", fontsize=12)
    plt.ylabel("Amount ($)", fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(alpha=0.3)

    img_line = io.BytesIO()
    plt.savefig(img_line, format='png', bbox_inches='tight')
    img_line.seek(0)
    img_line_base64 = base64.b64encode(img_line.getvalue()).decode('utf-8')
    plt.close()

    return render_template("financial_health.html", 
                           img_line_base64=img_line_base64, 
                           real_time_analytics=real_time_analytics, 
                           days=days, 
                           revenue=revenue, 
                           expenses=expenses, 
                           profit=profit,
                           financial_data=financial_data)
def generate_chart(data):
    product_names = [item["name"] for item in data]
    stock = [item["stock"] for item in data]

  
    # Create bar chart
    plt.figure(figsize=(8, 6))
    plt.bar(product_names, stock, color="skyblue")
    plt.title("Product Stock Chart")
    plt.xlabel("Products")
    plt.ylabel("Stock")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Save the chart as a base64 image
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    return chart_data
@visualization.route('/visualization/<category>')

def category_page(category):
    page = request.args.get('page', default=1, type=int)
    has_next = True  # Example logic for pagination

    inventory_data = {
    "accessories": {"products": [{"name": "Watch", "stock": 50}, {"name": "Belt", "stock": 30}], "title": "Accessories"},
    "kids": {"products": [{"name": "Toy", "stock": 60}, {"name": "Kids T-shirt", "stock": 40}], "title": "Kids"},
    "womens_fashion": {"products": [{"name": "Dress", "stock": 70}, {"name": "Handbag", "stock": 25}], "title": "Women's Fashion"},
    "fashion": {"products": [{"name": "Shirt", "stock": 80}, {"name": "T-shirt", "stock": 60}], "title": "Fashion"},
}
    if category in inventory_data:
        data = inventory_data[category]
        chart_data = generate_chart(data["products"])
        return render_template("category_page.html", category=category, title=data["title"], products=data["products"], chart_data=chart_data, page=page,  has_next=has_next,)
    return "Category not found", 404







@visualization.route('/inventory_status')
def inventory_status():
    # Static data for demonstration
    page = request.args.get('page', default=1, type=int)
    has_next = True  # Example logic for pagination

    categories = [
        ("Fashion", 150),
        ("Women's Fashion", 80),
        ("Kids", 120),
        ("Accessories", 60),
        ("others", 90)
    ]

    # Data for visualization
    category_labels = [category[0] for category in categories]
    category_stock = [category[1] for category in categories]

    # Analytics Data
    total_stock = sum(category_stock)
    max_stock_category = category_labels[category_stock.index(max(category_stock))]
    min_stock_category = category_labels[category_stock.index(min(category_stock))]

    analytics = {
        "Total Stock": total_stock,
        "Category with Max Stock": max_stock_category,
        "Category with Min Stock": min_stock_category,
    }
    

    # Default stock value
    default_stock = 2

    # Create a bar chart with a default stock line
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(category_labels, category_stock, color=plt.cm.Pastel1.colors)
    ax.axhline(y=default_stock, color='red', linestyle='--', linewidth=1.5, label=f"Default Stock: {default_stock}")
    ax.set_title("Stock Analytics by Category", fontsize=14)
    ax.set_xlabel("Categories")
    ax.set_ylabel("Total Stock (Quantity)")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend(loc='upper right')

    # Save chart as a base64 string
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()

    # Static product details
    products = [
        {"id": 1, "name": "Laptop", "category": "Electronics", "quantity": 50},
        {"id": 2, "name": "Chair", "category": "Furniture", "quantity": 30},
        {"id": 3, "name": "T-shirt", "category": "Clothing", "quantity": 70},
        {"id": 4, "name": "Novel", "category": "Books", "quantity": 20},
        {"id": 5, "name": "Action Figure", "category": "Toys", "quantity": 40}
    ]

    return render_template(
        "vinventory_status.html",
        page=page,
        chart_data=chart_data,
        has_next=has_next,
        analytics=analytics,
        products=products,
    )