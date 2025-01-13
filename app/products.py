import sqlite3
from flask import Blueprint,redirect, render_template, abort, request, flash, session 
from .models import *

products= Blueprint('products', __name__)


def get_products(user_id):
    """Fetch products and wishlist for the logged-in user."""
    conn = sqlite3.connect('instance/dbprofinal1.db')
    cursor = conn.cursor()
    
    # Fetch all products
    cursor.execute("SELECT product_id, name, manufacturer, price, image_url, gender, rating, is_featured FROM products")
    products = cursor.fetchall()
    cart = cursor.execute(
        "SELECT product_id FROM cart WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    # Fetch wishlist items for the user
    wishlist = cursor.execute(
        "SELECT product_id FROM wishlist WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    
    conn.close()
    
    # Return products and wishlist (wishlist as a list of product_id's)
    return products, [row[0] for row in wishlist],[row[0] for row in cart]
@products.route('/product/<int:product_id>')
def product_details(product_id):
    # Fetch the product by ID
    product = Product.query.get_or_404(product_id)

    # Pass the product details to the template
    return render_template('product_details.html', product=product)
@products.route('/')
def homepage():
    """Render the homepage with products and wishlist data."""
    user_id = session.get('user_id', 1)  # Replace 1 with the actual logged-in user_id
    from .products import get_products  # Import the get_products function

    # Fetch products and wishlist
    products, wishlist,cc= get_products(user_id)

    return render_template('home.html', products=products, wis=wishlist,cat=cc)

