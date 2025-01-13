from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import Product
main = Blueprint('main', __name__)

@main.route('/')
def home():
    products = Product.query.all()
    return render_template('home.html',products=products)
# @main.route('/customer_dashboard')
# def customer_dashboard():
#     return render_template('customer_dashboard.html')  # Create this template

# @main.route('/delivery_dashboard')
# def delivery_dashboard():
#     return render_template('delivery_dashboard.html')  # Create this template

# @main.route('/default_dashboard')
# def default_dashboard():
#     return render_template('default_dashboard.html')  # Create this template

# @main.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html')  # Fallback or general dashboard

