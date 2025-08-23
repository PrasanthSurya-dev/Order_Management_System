import os
import psycopg2
import sqlite3
import json
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

# App Configuration
app = Flask(__name__)
app.secret_key = 'a-very-strong-and-random-secret-key'

# Build DATABASE_URL manually for Supabase
DATABASE_URL = (
    "postgresql://postgres:gsAAswA5sK1q2NC7@db.ltbuxhvctkyivrvrzqyt.supabase.co:5432/postgres?sslmode=require"
)

# Helper function to determine database type
def is_postgres():
    return bool(DATABASE_URL)

# --- DATABASE CONNECTION ---
def get_db_connection():
    """Connects to PostgreSQL (Supabase) or SQLite (local)."""
    if is_postgres():
        return psycopg2.connect(DATABASE_URL)
    else:
        return sqlite3.connect("database.db")
    
# --- DATABASE INITIALIZATION ---
def init_db():
    # This function is now only for local SQLite setup.
    # The live database is set up with the postgres_populate.sql script.
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
            name TEXT, address TEXT, contact TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, price REAL,
            stock INTEGER, image_url TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER, items TEXT, total REAL,
            payment_method TEXT, delivery_date TEXT, status TEXT,
            cancellation_timestamp TEXT,order_date TEXT,actual_delivery_date TEXT, cancellation_refund TEXT)''')
        c.execute('INSERT OR IGNORE INTO admin (id, username, password) VALUES (1, "admin", "adminpass")')
        conn.commit()
        c.close()

# --- BACKGROUND TASK ---
def update_order_statuses():
    """Background task to automatically mark 'In Transit' orders as 'Delivered'."""
    while True:
        conn = get_db_connection()
        c = conn.cursor()
        today = datetime.now().date()
        
        # This is the corrected part
        placeholder = '%s' if is_postgres() else '?'
        
        c.execute(f"SELECT id, delivery_date FROM orders WHERE status = {placeholder}", ('In Transit',))
        for order in c.fetchall():
            order_id, delivery_str = order
            try:
                delivery_date = datetime.strptime(str(delivery_str), "%Y-%m-%d").date()
                if delivery_date <= today:
                    c.execute(f"UPDATE orders SET status={placeholder} WHERE id={placeholder}", ('Delivered', order_id))
            except (ValueError, TypeError):
                continue
        conn.commit()
        c.close()
        conn.close()
        time.sleep(3600)

def migrate_old_orders():
    # This is a one-time function to fix your old data
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, delivery_date FROM orders WHERE order_date IS NULL")
    orders_to_fix = c.fetchall()
    if orders_to_fix:
        placeholder = '%s' if is_postgres() else '?'
        for order_id, delivery_str in orders_to_fix:
            try:
                delivery_date = datetime.strptime(str(delivery_str), "%Y-%m-%d").date()
                order_date = (delivery_date - timedelta(days=3)).strftime("%Y-%m-%d")
                c.execute(f"UPDATE orders SET order_date = {placeholder} WHERE id = {placeholder}", (order_date, order_id))
            except (ValueError, TypeError):
                c.execute(f"UPDATE orders SET order_date = {placeholder} WHERE id = {placeholder}", ('2025-01-01', order_id))
        conn.commit()
    c.close()
    conn.close()

# --- AUTHENTICATION ROUTES ---
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].lower()
    password = request.form['password']
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    
    c.execute(f'SELECT id, password FROM customers WHERE username={placeholder}', (username,))
    user = c.fetchone()
    if user and user[1] == password:
        session['user_id'] = user[0]
        c.close()
        conn.close()
        return redirect(url_for('customer_dashboard'))
        
    c.execute(f'SELECT id, password FROM admin WHERE username={placeholder}', (username,))
    admin = c.fetchone()
    if admin and admin[1] == password:
        session['admin_id'] = admin[0]
        c.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))
        
    c.close()
    conn.close()
    flash('Invalid credentials')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            c = conn.cursor()
            username = request.form['username'].lower()
            placeholder = '%s' if is_postgres() else '?'
            sql = f'INSERT INTO customers (username, password, name, address, contact) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})'
            c.execute(sql, (username, request.form['password'], request.form['name'], request.form['address'], request.form['contact']))
            conn.commit()
            c.close()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('index'))
        except (psycopg2.IntegrityError, sqlite3.IntegrityError):
            flash('Username already exists.', 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- CUSTOMER-FACING ROUTES ---
@app.route('/customer')
def customer_dashboard():
    if 'user_id' not in session: return redirect(url_for('index'))
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    c.execute(f'SELECT name, address, contact FROM customers WHERE id={placeholder}', (session['user_id'],))
    customer = c.fetchone()
    c.close()
    conn.close()
    return render_template('customer_dashboard.html', customer_name=customer[0], customer_address=customer[1], customer_contact=customer[2])

# --- API ROUTES (for JavaScript) ---
@app.route('/get_products')
def get_products():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, name, price, stock, image_url FROM products')
    products = c.fetchall()
    c.close()
    conn.close()
    return jsonify([{'id': r[0], 'name': r[1], 'price': float(r[2]), 'stock': r[3], 'image_url': r[4]} for r in products])

@app.route('/get_orders')
def get_orders():
    if 'user_id' not in session: return jsonify([])
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    c.execute(f'''SELECT id, items, total, payment_method, delivery_date, 
                     status, actual_delivery_date, cancellation_refund 
                     FROM orders WHERE customer_id={placeholder} ORDER BY id DESC''', (session['user_id'],))
    orders_data = c.fetchall()
    
    c.execute("SELECT id, name FROM products")
    products_map = {p[0]: p[1] for p in c.fetchall()}
    c.close()
    conn.close()

    orders_list = []
    for r in orders_data:
        items_dict = json.loads(r[1])
        items_with_names = ", ".join([f"{products_map.get(int(pid), 'Unknown Product')} x {qty}" for pid, qty in items_dict.items()])
        orders_list.append({
            'id': r[0], 'items_text': items_with_names, 'total': float(r[2]), 'payment': r[3], 
            'delivery': str(r[4]), 'status': r[5], 'actual_delivery': str(r[6]), 'cancellation_refund': r[7]
        })
    return jsonify(orders_list)

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session: return jsonify({'status': 'fail'}), 403
    data = request.get_json()
    order_date = datetime.now().strftime("%Y-%m-%d")
    delivery_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")

    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    for pid, qty in data['cart'].items():
        c.execute(f'UPDATE products SET stock = stock - {placeholder} WHERE id = {placeholder}', (qty, pid))
    
    sql = f'INSERT INTO orders (customer_id, items, total, payment_method, delivery_date, status, order_date) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})'
    c.execute(sql, (session['user_id'], json.dumps(data['cart']), data['total'], data['payment'], delivery_date, "Order Received", order_date))
    conn.commit()
    c.close()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/confirm_cancel/<int:order_id>')
def confirm_cancel_order(order_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('cancel_confirmation.html', order_id=order_id)

@app.route('/process_cancellation', methods=['POST'])
def process_cancellation():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    order_id = request.form['order_id']
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    c.execute(f'SELECT items, payment_method FROM orders WHERE id={placeholder} AND customer_id={placeholder}', (order_id, session['user_id']))
    order_row = c.fetchone()
    if not order_row:
        flash("Could not cancel order.", "error")
        return redirect(url_for('customer_dashboard') + '#orders')
    
    items, payment_method = json.loads(order_row[0]), order_row[1]
    for pid, qty in items.items():
        c.execute(f'UPDATE products SET stock = stock + {placeholder} WHERE id = {placeholder}', (qty, pid))
    
    cancellation_time = datetime.now().isoformat()
    cancellation_refund = ""
    if payment_method != 'Cash on Delivery':
        cancellation_refund = "Your order has been cancelled. Your refund will be processed within 2 business days to your account."
    c.execute(f'UPDATE orders SET status={placeholder}, cancellation_timestamp={placeholder}, cancellation_refund={placeholder} WHERE id={placeholder}',
               ("Cancelled", cancellation_time, cancellation_refund, order_id))
    conn.commit()
    c.close()
    conn.close()
    flash(f"Order #{order_id} has been successfully cancelled.", "success")
    return redirect(url_for('customer_dashboard') + '#orders')

# --- ADMIN ROUTES ---
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session: return redirect(url_for('index'))
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    
    c.execute(f"SELECT SUM(total) FROM orders WHERE order_date = {placeholder} AND status != 'Cancelled'",(today_str,))
    sales_today = c.fetchone()[0] or 0
    c.execute(f"SELECT COUNT(id) FROM orders WHERE order_date = {placeholder}",(today_str,))
    orders_today = c.fetchone()[0]
    c.execute("SELECT COUNT(id) FROM orders WHERE status NOT IN ('Delivered', 'Cancelled')")
    pending_orders = c.fetchone()[0]
    c.execute("SELECT COUNT(id) FROM products WHERE stock < 50 AND stock >= 0")
    low_stock_items = c.fetchone()[0]
    c.execute('''
        SELECT COUNT(id) FROM orders WHERE status = 'Cancelled'
        AND payment_method != 'Cash on Delivery'
        AND (cancellation_refund IS NULL OR cancellation_refund NOT LIKE '%%initiated%%')
    ''')
    awaiting_refund_count = c.fetchone()[0]

    current_month_start = today.strftime('%Y-%m-01')
    c.execute(f"SELECT SUM(total) FROM orders WHERE status != 'Cancelled' AND order_date >= {placeholder}", (current_month_start,))
    current_rev = c.fetchone()[0] or 0
    c.execute(f"SELECT COUNT(id) FROM orders WHERE status != 'Cancelled' AND order_date >= {placeholder}", (current_month_start,))
    current_orders = c.fetchone()[0] or 1
    current_aov = current_rev / current_orders

    last_month_end = today.replace(day=1) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    sql = f"SELECT SUM(total) FROM orders WHERE status != 'Cancelled' AND order_date BETWEEN {placeholder} AND {placeholder}"
    c.execute(sql, (last_month_start.strftime('%Y-%m-%d'), last_month_end.strftime('%Y-%m-%d')))
    prev_rev = c.fetchone()[0] or 0
    sql = f"SELECT COUNT(id) FROM orders WHERE status != 'Cancelled' AND order_date BETWEEN {placeholder} AND {placeholder}"
    c.execute(sql, (last_month_start.strftime('%Y-%m-%d'), last_month_end.strftime('%Y-%m-%d')))
    prev_orders = c.fetchone()[0] or 1
    previous_aov = prev_rev / prev_orders
    
    aov_change = 0
    if previous_aov > 0:
        aov_change = ((current_aov - previous_aov) / previous_aov) * 100
    
    c.close()
    conn.close()
    return render_template('admin_dashboard.html', 
                           sales_today=float(sales_today),
                           orders_today=orders_today,
                           pending_orders=pending_orders,
                           low_stock_items=low_stock_items,
                           awaiting_refund_count=awaiting_refund_count,
                           average_order_value=float(current_aov),
                           aov_change=aov_change)

@app.route('/admin/orders')
def admin_orders():
    if 'admin_id' not in session: return redirect(url_for('index'))
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    filter_date = request.args.get('filter_date', '')
    filter_status = request.args.get('filter_status', '')

    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    
    query = 'SELECT o.id, c.name, o.items, c.address, o.payment_method, o.status, o.total FROM orders o JOIN customers c ON o.customer_id = c.id'
    conditions = []
    params = []
    
    if search:
        like_op = 'ILIKE' if is_postgres() else 'LIKE'
        conditions.append(f"(c.name {like_op} {placeholder} OR o.id = {placeholder})")
        params.extend([f'%{search}%', search])
    
    if status_filter:
        conditions.append(f"o.status = {placeholder}")
        params.append(status_filter)
    
    if filter_date == 'today':
        today_str = datetime.now().strftime("%Y-%m-%d")
        conditions.append(f"o.order_date = {placeholder}")
        params.append(today_str)
        
    if filter_status == 'pending':
        conditions.append("o.status IN ('Order Received', 'Shipped', 'In Transit')")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY o.id DESC"
    
    c.execute(query, tuple(params))
    orders = c.fetchall()
    c.close()
    conn.close()
    
    return render_template('admin_orders.html', 
                           orders=orders, 
                           search_query=search, 
                           status_filter=status_filter)

@app.route('/admin/order/<int:order_id>')
def admin_order_detail(order_id):
    if 'admin_id' not in session: return redirect(url_for('index'))
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    
    sql = f'''SELECT o.id, o.items, o.total, o.payment_method, o.delivery_date, 
                     o.status, c.name, c.address, c.contact, o.actual_delivery_date, o.cancellation_refund 
                     FROM orders o JOIN customers c ON o.customer_id = c.id 
                     WHERE o.id = {placeholder}'''
    c.execute(sql, (order_id,))
    order = c.fetchone()
    
    c.execute('SELECT id, name FROM products')
    products = c.fetchall()
    c.close()
    conn.close()

    if not order:
        flash(f"Order ID {order_id} not found.", "error")
        return redirect(url_for('admin_orders'))

    product_map = {p[0]: p[1] for p in products}
    items = [{'name': product_map.get(int(pid), "Unknown"), 'quantity': qty} for pid, qty in json.loads(order[1]).items()]
    
    return render_template('admin_order_detail.html', order=order, items=items)

@app.route('/admin/order/update_status', methods=['POST'])
def update_order_status():
    if 'admin_id' not in session: return redirect(url_for('index'))
    order_id, new_status = request.form['order_id'], request.form['status']

    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    
    if new_status == 'Delivered':
        actual_date = datetime.now().strftime("%Y-%m-%d")
        c.execute(f'UPDATE orders SET status={placeholder}, actual_delivery_date={placeholder} WHERE id={placeholder}', (new_status, actual_date, order_id))
    else:
        c.execute(f'UPDATE orders SET status={placeholder} WHERE id={placeholder}', (new_status, order_id))
    conn.commit()
    c.close()
    conn.close()
    
    flash(f"Order #{order_id} status updated to '{new_status}'.", 'success')
    return redirect(url_for('admin_order_detail', order_id=order_id))

@app.route('/admin/order/process_refund', methods=['POST'])
def process_refund():
    if 'admin_id' not in session:
        return redirect(url_for('index'))
    
    order_id = request.form['order_id']
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    
    new_reason = "Refund initiated successfully to your account."
    c.execute(f"UPDATE orders SET cancellation_refund = {placeholder} WHERE id = {placeholder}", (new_reason, order_id))
    conn.commit()
    c.close()
    conn.close()

    flash(f"Refund for Order #{order_id} has been marked as processed.", "success")
    return redirect(url_for('admin_order_detail', order_id=order_id))

@app.route('/admin/awaiting_refund')
def admin_awaiting_refund():
    if 'admin_id' not in session: return redirect(url_for('index'))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT o.id, c.name, o.total, o.order_date
        FROM orders o JOIN customers c ON o.customer_id = c.id
        WHERE o.status = 'Cancelled'
        AND o.payment_method != 'Cash on Delivery'
        AND (o.cancellation_refund IS NULL OR o.cancellation_refund NOT LIKE '%%initiated%%')
        ORDER BY o.id DESC
    ''')
    awaiting_refund_orders = c.fetchall()
    c.close()
    conn.close()
    return render_template('admin_awaiting_refund.html', orders=awaiting_refund_orders)

@app.route('/admin/products')
def admin_products():
    if 'admin_id' not in session: return redirect(url_for('index'))
    filter_stock = request.args.get('filter_stock', '')
    conn = get_db_connection()
    c = conn.cursor()
    
    query = 'SELECT id, name, description, price, stock, image_url FROM products'
    params = []

    if filter_stock == 'low':
        query += ' WHERE stock < 50 AND stock >= 0'

    query += ' ORDER BY id'
    c.execute(query, tuple(params))
    products = c.fetchall()
    c.close()
    conn.close()
    
    return render_template('admin_products.html', products=products)

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    if 'admin_id' not in session: return redirect(url_for('index'))
    form = request.form
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    
    sql = f'INSERT INTO products (name, description, price, stock, image_url) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})'
    c.execute(sql, (form['name'], form['description'], form['price'], form['stock'], form['image_url']))
    conn.commit()
    c.close()
    conn.close()
    flash(f"Product '{form['name']}' added.", 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/edit_product/<int:product_id>')
def edit_product(product_id):
    if 'admin_id' not in session: return redirect(url_for('index'))
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    
    c.execute(f'SELECT id, name, description, price, stock, image_url FROM products WHERE id = {placeholder}', (product_id,))
    product = c.fetchone()
    c.close()
    conn.close()
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin_products'))
    return render_template('admin_edit_product.html', product=product)

@app.route('/admin/update_product', methods=['POST'])
def update_product():
    if 'admin_id' not in session: return redirect(url_for('index'))
    form = request.form
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    
    sql = f'UPDATE products SET name={placeholder}, description={placeholder}, price={placeholder}, stock={placeholder}, image_url={placeholder} WHERE id={placeholder}'
    c.execute(sql, (form['name'], form['description'], form['price'], form['stock'], form['image_url'], form['product_id']))
    conn.commit()
    c.close()
    conn.close()
    flash(f"Product '{form['name']}' updated.", 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/delete_product', methods=['POST'])
def delete_product():
    if 'admin_id' not in session: return redirect(url_for('index'))
    product_id = request.form['product_id']
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    
    c.execute(f'DELETE FROM products WHERE id = {placeholder}', (product_id,))
    conn.commit()
    c.close()
    conn.close()
    flash(f'Product ID #{product_id} deleted.', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/customers')
def admin_customers():
    if 'admin_id' not in session:
        return redirect(url_for('index'))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, name, username, contact, address FROM customers ORDER BY id')
    customers = c.fetchall()
    c.close()
    conn.close()
    return render_template('admin_customers_list.html', customers=customers)

@app.route('/admin/customer/<int:customer_id>')
def admin_customer_detail(customer_id):
    if 'admin_id' not in session:
        return redirect(url_for('index'))
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    
    c.execute(f'SELECT id, name, username, contact, address FROM customers WHERE id = {placeholder}', (customer_id,))
    customer = c.fetchone()
    if not customer:
        flash('Customer not found.', 'error')
        return redirect(url_for('admin_customers'))

    c.execute(f'SELECT id, order_date, total, status FROM orders WHERE customer_id = {placeholder} ORDER BY id DESC', (customer_id,))
    orders = c.fetchall()

    c.execute(f"SELECT SUM(total) FROM orders WHERE customer_id = {placeholder} AND status != 'Cancelled'", (customer_id,))
    total_spent = c.fetchone()[0] or 0
    total_orders = len(orders)
    aov = total_spent / total_orders if total_orders > 0 else 0
    analytics = {'total_spent': float(total_spent), 'total_orders': total_orders, 'aov': float(aov)}
    c.close()
    conn.close()
    return render_template('admin_customer_detail.html', 
                           customer=customer, 
                           orders=orders,
                           analytics=analytics)

@app.route('/admin/reports')
def admin_reports():
    if 'admin_id' not in session:
        return redirect(url_for('index'))
    date_range = request.args.get('range', '7days')
    conn = get_db_connection()
    c = conn.cursor()
    placeholder = '%s' if is_postgres() else '?'
    
    # Top Selling Products
    if is_postgres():
        c.execute('''
            SELECT p.name, SUM(CAST(je.value AS INTEGER)) as total_sold
            FROM orders o, jsonb_each_text(o.items) je
            JOIN products p ON p.id = CAST(je.key AS INTEGER)
            WHERE o.status != 'Cancelled' AND o.order_date IS NOT NULL
            GROUP BY p.name ORDER BY total_sold DESC LIMIT 10
        ''')
    else:
        c.execute('''
            SELECT p.name, SUM(CAST(je.value AS INTEGER)) as total_sold
            FROM orders o, json_each(o.items) je
            JOIN products p ON p.id = CAST(je.key AS INTEGER)
            WHERE o.status != 'Cancelled' AND o.order_date IS NOT NULL
            GROUP BY p.name ORDER BY total_sold DESC LIMIT 10
        ''')
    top_selling_products = c.fetchall()

    # Sales Chart
    sales_data_dict = {}
    if date_range == 'all':
        sql = "SELECT to_char(order_date, 'YYYY-MM') as month, SUM(total) FROM orders WHERE status != 'Cancelled' AND order_date IS NOT NULL GROUP BY month ORDER BY month" if is_postgres() else "SELECT strftime('%Y-%m', order_date) as month, SUM(total) FROM orders WHERE status != 'Cancelled' AND order_date IS NOT NULL GROUP BY month ORDER BY month"
        c.execute(sql)
        all_sales = c.fetchall()
        for month, total in all_sales:
            sales_data_dict[month] = total
    else:
        days = 7 if date_range == '7days' else 30
        start_date = datetime.now().date() - timedelta(days=days - 1)
        for i in range(days):
            day = start_date + timedelta(days=i)
            sales_data_dict[day.strftime("%Y-%m-%d")] = 0
        sql = f"SELECT order_date, SUM(total) FROM orders WHERE order_date >= {placeholder} AND status != 'Cancelled' GROUP BY order_date"
        c.execute(sql, (start_date.strftime("%Y-%m-%d"),))
        daily_sales_data = c.fetchall()
        for date_str, total in daily_sales_data:
            date_key = str(date_str)
            if date_key in sales_data_dict:
                sales_data_dict[date_key] = total
    
    sorted_keys = sorted(sales_data_dict.keys())
    labels = [(datetime.strptime(key, "%Y-%m").strftime("%b %Y") if date_range == 'all' else datetime.strptime(key, "%Y-%m-%d").strftime("%b %d")) for key in sorted_keys]
    values = [float(sales_data_dict[key]) for key in sorted_keys]
    sales_chart_data = {"labels": labels, "values": values}
    
    # Pie Chart
    all_statuses = ['Order Received', 'Shipped', 'In Transit', 'Delivered', 'Cancelled']
    status_counts = {status: 0 for status in all_statuses}
    c.execute('SELECT status, COUNT(id) FROM orders GROUP BY status')
    status_distribution_from_db = c.fetchall()
    for status, count in status_distribution_from_db:
        if status in status_counts:
            status_counts[status] = count
    pie_chart_data = {"labels": list(status_counts.keys()), "values": list(status_counts.values())}

    # Payment Distribution
    c.execute("SELECT COUNT(id) FROM orders WHERE status != 'Cancelled'")
    total_valid_orders = c.fetchone()[0] or 1
    c.execute("SELECT payment_method, COUNT(id) FROM orders WHERE status != 'Cancelled' GROUP BY payment_method")
    payment_data_from_db = c.fetchall()
    valid_methods = ['Cash on Delivery', 'UPI', 'Credit Card', 'Debit Card']
    payment_counts = {method: 0 for method in valid_methods}
    for method, count in payment_data_from_db:
        if method in payment_counts:
            payment_counts[method] = count
    payment_distribution = []
    if total_valid_orders > 0:
        for method, count in payment_counts.items():
            percentage = (count / total_valid_orders) * 100
            payment_distribution.append({"method": method, "percentage": round(percentage, 1)})
    
    c.close()
    conn.close()
    return render_template('admin_reports.html', 
                           top_products=top_selling_products,
                           sales_data=sales_chart_data,
                           pie_data=pie_chart_data,
                           payment_distribution=payment_distribution,
                           active_range=date_range)

@app.route('/admin/reports/aov')
def admin_aov_report():
    if 'admin_id' not in session:
        return redirect(url_for('index'))
    conn = get_db_connection()
    c = conn.cursor()
    
    aov_by_month = {}
    today = datetime.now()
    for i in range(12):
        current_month = today - timedelta(days=i * 30)
        month_key = current_month.strftime('%Y-%m')
        
        if is_postgres():
            sql = "SELECT SUM(total), COUNT(id) FROM orders WHERE to_char(order_date, 'YYYY-MM') = %s AND status != 'Cancelled'"
        else:
            sql = "SELECT SUM(total), COUNT(id) FROM orders WHERE strftime('%Y-%m', order_date) = ? AND status != 'Cancelled'"
        
        c.execute(sql, (month_key,))
        month_data = c.fetchone()
        
        revenue, orders_count = (month_data[0] or 0), (month_data[1] or 1)
        aov = revenue / orders_count
        aov_by_month[month_key] = aov

    sorted_months = sorted(aov_by_month.keys())
    aov_trend_data = {
        "labels": [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in sorted_months],
        "values": [float(aov_by_month[m]) for m in sorted_months]
    }
    c.close()
    conn.close()
    return render_template('admin_aov_report.html', aov_trend_data=aov_trend_data)

# --- START THE APP ---
if __name__ == '__main__':
    print("Starting Flask app in local debug mode...")
    if not is_postgres():
        init_db()
        migrate_old_orders()
    threading.Thread(target=update_order_statuses, daemon=True).start()
    app.run(host='0.0.0.0', port=8080, debug=True)