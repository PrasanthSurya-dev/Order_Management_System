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
DATABASE = 'database.db'

# --- DATABASE INITIALIZATION ---
def init_db():
    with sqlite3.connect(DATABASE) as conn:
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
            cancellation_timestamp TEXT,order_date TEXT,actual_delivery_date TEXT)''')
        c.execute('INSERT OR IGNORE INTO admin (id, username, password) VALUES (1, "admin", "adminpass")')
        conn.commit()

def get_db_connection():
    # Render (and other hosts) sets a DATABASE_URL environment variable
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Connect to the live PostgreSQL database
        conn = psycopg2.connect(db_url)
    else:
        # Connect to the local SQLite database file
        conn = sqlite3.connect(DATABASE)
    return conn

# --- BACKGROUND TASK ---
def update_order_statuses():
    while True:
        with get_db_connection() as conn:
            c = conn.cursor()
            today = datetime.now().date()
            c.execute("SELECT id, delivery_date FROM orders WHERE status = 'In Transit'")
            for order in c.fetchall():
                order_id, delivery_str = order
                delivery_date = datetime.strptime(delivery_str, "%Y-%m-%d").date()
                if delivery_date <= today:
                    c.execute("UPDATE orders SET status=? WHERE id=?", ('Delivered', order_id))
            conn.commit()
        time.sleep(3600)

def migrate_old_orders():
    # This is a new one-time function to fix your old data
    with get_db_connection() as conn:
        c = conn.cursor()
        # Find all orders that are missing an order_date
        c.execute("SELECT id, delivery_date FROM orders WHERE order_date IS NULL")
        orders_to_fix = c.fetchall()
        if orders_to_fix:
            print(f"Found {len(orders_to_fix)} old orders to fix. Applying migration...")
            for order_id, delivery_str in orders_to_fix:
                try:
                    # Guess the order date was 3 days before the delivery date
                    delivery_date = datetime.strptime(delivery_str, "%Y-%m-%d").date()
                    order_date = (delivery_date - timedelta(days=3)).strftime("%Y-%m-%d")
                    c.execute("UPDATE orders SET order_date = ? WHERE id = ?", (order_date, order_id))
                except (ValueError, TypeError):
                    # If date is invalid, just set it to a default past date
                    c.execute("UPDATE orders SET order_date = '2025-01-01' WHERE id = ?", (order_id,))
            conn.commit()
            print("Migration complete.")

# --- AUTHENTICATION ROUTES ---
@app.route('/')
def index():
    return render_template('login.html')

# In the login() function
@app.route('/login', methods=['POST'])
def login():
    # This forces the login attempt to be lowercase
    username = request.form['username'].lower()
    password = request.form['password']

    with get_db_connection() as conn:
        user = conn.execute('SELECT id FROM customers WHERE username=? AND password=?', (username, password)).fetchone()
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('customer_dashboard'))
        admin = conn.execute('SELECT id FROM admin WHERE username=? AND password=?', (username, password)).fetchone()
        if admin:
            session['admin_id'] = admin[0]
            return redirect(url_for('admin_dashboard'))
    flash('Invalid credentials')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            with get_db_connection() as conn:
                # This forces the username to be saved as lowercase
                username = request.form['username'].lower()
                conn.execute('INSERT INTO customers (username, password, name, address, contact) VALUES (?, ?, ?, ?, ?)',
                          (username, request.form['password'], request.form['name'], request.form['address'], request.form['contact']))
                conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('index'))
        except psycopg2.IntegrityError:
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
    with get_db_connection() as conn:
        customer = conn.execute('SELECT name, address, contact FROM customers WHERE id=?', (session['user_id'],)).fetchone()
    return render_template('customer_dashboard.html', customer_name=customer[0], customer_address=customer[1], customer_contact=customer[2])

# --- API ROUTES (for JavaScript) ---
@app.route('/get_products')
def get_products():
    with get_db_connection() as conn:
        products = conn.execute('SELECT id, name, price, stock, image_url FROM products').fetchall()
    return jsonify([{'id': r[0], 'name': r[1], 'price': r[2], 'stock': r[3], 'image_url': r[4]} for r in products])

@app.route('/get_orders')
def get_orders():
    if 'user_id' not in session: return jsonify([])
    with get_db_connection() as conn:
        c = conn.cursor()
        orders_data = c.execute('''SELECT id, items, total, payment_method, delivery_date, 
                                        status, actual_delivery_date, cancellation_refund 
                                 FROM orders WHERE customer_id=? ORDER BY id DESC''', (session['user_id'],)).fetchall()
        
        # Get all product names in one query for efficiency
        products_map = {p[0]: p[1] for p in c.execute("SELECT id, name FROM products").fetchall()}

        # Build the final response
        orders_list = []
        for r in orders_data:
            items_dict = json.loads(r[1])
            # Create a new items string with real names, e.g., "Wireless Earbuds x 1"
            items_with_names = ", ".join([f"{products_map.get(int(pid), 'Unknown Product')} x {qty}" for pid, qty in items_dict.items()])
            
            orders_list.append({
                'id': r[0], 
                'items_text': items_with_names, 
                'total': r[2], 
                'payment': r[3], 
                'delivery': r[4], 
                'status': r[5], 
                'actual_delivery': r[6], 
                'cancellation_refund': r[7]
            })
    return jsonify(orders_list) 
    return jsonify([{'id': r[0], 'items': json.loads(r[1]), 'total': r[2], 'payment': r[3], 
                     'delivery': r[4], 'status': r[5], 'actual_delivery': r[6], 'cancel_refund': r[7]} for r in orders])
@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session: return jsonify({'status': 'fail'}), 403
    data = request.get_json()
    
    order_date = datetime.now().strftime("%Y-%m-%d")
    # Set the initial ESTIMATED delivery date to 4 days in the future
    delivery_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")

    with get_db_connection() as conn:
        for pid, qty in data['cart'].items():
            conn.execute('UPDATE products SET stock = stock - ? WHERE id = ?', (qty, pid))
        
        conn.execute(
            'INSERT INTO orders (customer_id, items, total, payment_method, delivery_date, status, order_date) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (session['user_id'], json.dumps(data['cart']), data['total'], data['payment'], delivery_date, "Order Received", order_date)
        )
        conn.commit()
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
    with get_db_connection() as conn:
        order_row = conn.execute('SELECT items, payment_method FROM orders WHERE id=? AND customer_id=?', (order_id, session['user_id'])).fetchone()
        if not order_row:
            flash("Could not cancel order.", "error")
            return redirect(url_for('customer_dashboard') + '#orders')
        
        items, payment_method = json.loads(order_row[0]), order_row[1]
        for pid, qty in items.items():
            conn.execute('UPDATE products SET stock = stock + ? WHERE id = ?', (qty, pid))
        
        cancellation_time = datetime.now().isoformat()

        # logic for cancellation refund
        cancellation_refund = ""
        if payment_method != 'Cash on Delivery':
            cancellation_refund = "Your order has been cancelled. Your refund will be processed within 2 business days to your account."

        conn.execute('UPDATE orders SET status=?, cancellation_timestamp=?, cancellation_refund=? WHERE id=?',
                     ("Cancelled", cancellation_time, cancellation_refund, order_id))
        conn.commit()

    flash(f"Order #{order_id} has been successfully cancelled.", "success")
    return redirect(url_for('customer_dashboard') + '#orders')

@app.route('/admin/order/process_refund', methods=['POST'])
def process_refund():
    if 'admin_id' not in session:
        return redirect(url_for('index'))
    
    order_id = request.form['order_id']
    with get_db_connection() as conn:
        # Update the reason to show the refund has been processed
        new_reason = "Refund initiated successfully to your account."
        conn.execute("UPDATE orders SET cancellation_refund = ? WHERE id = ?", (new_reason, order_id))
        conn.commit()

    flash(f"Refund for Order #{order_id} has been marked as processed.", "success")
    return redirect(url_for('admin_order_detail', order_id=order_id))

# --- ADMIN ROUTES ---
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session: return redirect(url_for('index'))
    with get_db_connection() as conn:
        c = conn.cursor()
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        
        # Widget Queries
        sales_today = c.execute("SELECT SUM(total) FROM orders WHERE order_date = ? AND status != 'Cancelled'",(today_str,)).fetchone()[0] or 0
        orders_today = c.execute("SELECT COUNT(id) FROM orders WHERE order_date = ?",(today_str,)).fetchone()[0]
        pending_orders = c.execute("SELECT COUNT(id) FROM orders WHERE status NOT IN ('Delivered', 'Cancelled')").fetchone()[0]
        low_stock_items = c.execute("SELECT COUNT(id) FROM products WHERE stock < 50 AND stock >= 0").fetchone()[0]
        awaiting_refund_count = c.execute('''
            SELECT COUNT(id) FROM orders WHERE status = 'Cancelled'
            AND payment_method != 'Cash on Delivery'
            AND (cancellation_refund IS NULL OR cancellation_refund NOT LIKE '%initiated%')
        ''').fetchone()[0]

        # AOV Calculation
        current_month_start = today.strftime('%Y-%m-01')
        current_rev = c.execute("SELECT SUM(total) FROM orders WHERE status != 'Cancelled' AND order_date >= ?", (current_month_start,)).fetchone()[0] or 0
        current_orders = c.execute("SELECT COUNT(id) FROM orders WHERE status != 'Cancelled' AND order_date >= ?", (current_month_start,)).fetchone()[0] or 1
        current_aov = current_rev / current_orders

        last_month_end = today.replace(day=1) - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        prev_rev = c.execute("SELECT SUM(total) FROM orders WHERE status != 'Cancelled' AND order_date BETWEEN ? AND ?", (last_month_start.strftime('%Y-%m-%d'), last_month_end.strftime('%Y-%m-%d'))).fetchone()[0] or 0
        prev_orders = c.execute("SELECT COUNT(id) FROM orders WHERE status != 'Cancelled' AND order_date BETWEEN ? AND ?", (last_month_start.strftime('%Y-%m-%d'), last_month_end.strftime('%Y-%m-%d'))).fetchone()[0] or 1
        previous_aov = prev_rev / prev_orders
        
        aov_change = 0
        if previous_aov > 0:
            aov_change = ((current_aov - previous_aov) / previous_aov) * 100
        
    return render_template('admin_dashboard.html', 
                           sales_today=sales_today,
                           orders_today=orders_today,
                           pending_orders=pending_orders,
                           low_stock_items=low_stock_items,
                           awaiting_refund_count=awaiting_refund_count,
                           average_order_value=current_aov,
                           aov_change=aov_change)

@app.route('/admin/orders')
def admin_orders():
    if 'admin_id' not in session: return redirect(url_for('index'))
    
    # Get all possible filters from the URL
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    filter_date = request.args.get('filter_date', '')
    filter_status = request.args.get('filter_status', '')

    with get_db_connection() as conn:
        query = 'SELECT o.id, c.name, o.items, c.address, o.payment_method, o.status, o.total FROM orders o JOIN customers c ON o.customer_id = c.id'
        conditions = []
        params = []
        
        if search:
            conditions.append("(c.name LIKE ? OR o.id = ?)")
            params.extend([f'%{search}%', search])
        
        if status_filter:
            conditions.append("o.status = ?")
            params.append(status_filter)
        
        if filter_date == 'today':
            today_str = datetime.now().strftime("%Y-%m-%d")
            conditions.append("o.order_date = ?")
            params.append(today_str)
            
        if filter_status == 'pending':
            conditions.append("o.status IN ('Order Received', 'Shipped', 'In Transit')")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY o.id DESC"
        
        orders = conn.execute(query, tuple(params)).fetchall()
        
    return render_template('admin_orders.html', 
                           orders=orders, 
                           search_query=search, 
                           status_filter=status_filter)

@app.route('/admin/order/<int:order_id>')
def admin_order_detail(order_id):
    if 'admin_id' not in session: return redirect(url_for('index'))
    with get_db_connection() as conn:
        order = conn.execute('''SELECT 
                                o.id, o.items, o.total, o.payment_method, o.delivery_date, 
                                o.status, c.name, c.address, c.contact, o.actual_delivery_date, o.cancellation_refund 
                                FROM orders o JOIN customers c ON o.customer_id = c.id 
                                WHERE o.id = ?''', (order_id,)).fetchone()
        
        products = conn.execute('SELECT id, name FROM products').fetchall()

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

    with get_db_connection() as conn:
        # If the admin sets the status to "Delivered", save today's date
        if new_status == 'Delivered':
            actual_date = datetime.now().strftime("%Y-%m-%d")
            conn.execute('UPDATE orders SET status=?, actual_delivery_date=? WHERE id=?', (new_status, actual_date, order_id))
        else:
            # For any other status, just update the status
            conn.execute('UPDATE orders SET status=? WHERE id=?', (new_status, order_id))
        conn.commit()
        
    flash(f"Order #{order_id} status updated to '{new_status}'.", 'success')
    return redirect(url_for('admin_order_detail', order_id=order_id))

@app.route('/admin/awaiting_refund')
def admin_awaiting_refund():
    if 'admin_id' not in session: return redirect(url_for('index'))
    with get_db_connection() as conn:
        awaiting_refund_orders = conn.execute('''
            SELECT o.id, c.name, o.total, o.order_date
            FROM orders o JOIN customers c ON o.customer_id = c.id
            WHERE o.status = 'Cancelled'
            AND o.payment_method != 'Cash on Delivery'
            AND (o.cancellation_refund IS NULL OR o.cancellation_refund NOT LIKE '%initiated%')
            ORDER BY o.id DESC
        ''').fetchall()
    return render_template('admin_awaiting_refund.html', orders=awaiting_refund_orders)

@app.route('/admin/products')
def admin_products():
    if 'admin_id' not in session: return redirect(url_for('index'))

    # --- New Filter ---
    filter_stock = request.args.get('filter_stock', '')

    with get_db_connection() as conn:
        query = 'SELECT id, name, description, price, stock, image_url FROM products'
        params = []

        if filter_stock == 'low':
            query += ' WHERE stock < 50 AND stock >= 0'

        query += ' ORDER BY id'
        products = conn.execute(query, tuple(params)).fetchall()
        
    return render_template('admin_products.html', products=products)

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    if 'admin_id' not in session: return redirect(url_for('index'))
    form = request.form
    with get_db_connection() as conn:
        conn.execute('INSERT INTO products (name, description, price, stock, image_url) VALUES (?, ?, ?, ?, ?)',
                  (form['name'], form['description'], form['price'], form['stock'], form['image_url']))
        conn.commit()
    flash(f"Product '{form['name']}' added.", 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/edit_product/<int:product_id>')
def edit_product(product_id):
    if 'admin_id' not in session: return redirect(url_for('index'))
    with get_db_connection() as conn:
        product = conn.execute('SELECT id, name, description, price, stock, image_url FROM products WHERE id = ?', (product_id,)).fetchone()
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin_products'))
    return render_template('admin_edit_product.html', product=product)

@app.route('/admin/update_product', methods=['POST'])
def update_product():
    if 'admin_id' not in session: return redirect(url_for('index'))
    form = request.form
    with get_db_connection() as conn:
        conn.execute('UPDATE products SET name=?, description=?, price=?, stock=?, image_url=? WHERE id=?',
                  (form['name'], form['description'], form['price'], form['stock'], form['image_url'], form['product_id']))
        conn.commit()
    flash(f"Product '{form['name']}' updated.", 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/delete_product', methods=['POST'])
def delete_product():
    if 'admin_id' not in session: return redirect(url_for('index'))
    product_id = request.form['product_id']
    with get_db_connection() as conn:
        conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
    flash(f'Product ID #{product_id} deleted.', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/customers')
def admin_customers():
    if 'admin_id' not in session:
        return redirect(url_for('index'))

    with get_db_connection() as conn:
        customers = conn.execute('SELECT id, name, username, contact, address FROM customers ORDER BY id').fetchall()
        
    return render_template('admin_customers_list.html', customers=customers)

@app.route('/admin/customer/<int:customer_id>')
def admin_customer_detail(customer_id):
    if 'admin_id' not in session:
        return redirect(url_for('index'))

    with get_db_connection() as conn:
        customer = conn.execute('SELECT id, name, username, contact, address FROM customers WHERE id = ?', (customer_id,)).fetchone()
        if not customer:
            flash('Customer not found.', 'error')
            return redirect(url_for('admin_customers'))

        # Fetch all orders for this specific customer
        orders = conn.execute('SELECT id, order_date, total, status FROM orders WHERE customer_id = ? ORDER BY id DESC', (customer_id,)).fetchall()

        # --- New Customer Analytics Calculation ---
        customer_analytics = {}
        # 1. Total Money Spent (Lifetime Value)
        total_spent = conn.execute("SELECT SUM(total) FROM orders WHERE customer_id = ? AND status != 'Cancelled'", (customer_id,)).fetchone()[0] or 0
        customer_analytics['total_spent'] = total_spent
        
        # 2. Total Orders Placed
        total_orders = len(orders)
        customer_analytics['total_orders'] = total_orders
        
        # 3. Average Order Value (AOV) for this customer
        customer_analytics['aov'] = total_spent / total_orders if total_orders > 0 else 0
        # --- End of Analytics Calculation ---

    return render_template('admin_customer_detail.html', 
                           customer=customer, 
                           orders=orders,
                           analytics=customer_analytics) # Pass new analytics data

@app.route('/admin/reports')
def admin_reports():
    if 'admin_id' not in session:
        return redirect(url_for('index'))

    date_range = request.args.get('range', '7days')

    with get_db_connection() as conn:
        # --- Top Selling & Chart Logic (No Changes) ---
        # ... (Your existing correct logic for top_products, sales_chart_data, pie_chart_data) ...
        top_selling_products = conn.execute('''
            SELECT p.name, SUM(CAST(je.value AS INTEGER)) as total_sold
            FROM orders o, json_each(o.items) je
            JOIN products p ON p.id = CAST(je.key AS INTEGER)
            WHERE o.status != 'Cancelled' AND o.order_date IS NOT NULL
            GROUP BY p.name ORDER BY total_sold DESC LIMIT 10
        ''').fetchall()

        sales_data_dict = {}
        if date_range == 'all':
            all_sales = c.execute('''
                SELECT strftime('%Y-%m', order_date) as month, SUM(total)
                FROM orders WHERE status != 'Cancelled' AND order_date IS NOT NULL
                GROUP BY month ORDER BY month
            ''').fetchall()
            for month, total in all_sales:
                sales_data_dict[month] = total
        else:
            days = 7 if date_range == '7days' else 30
            start_date = datetime.now().date() - timedelta(days=days - 1)
            for i in range(days):
                day = start_date + timedelta(days=i)
                sales_data_dict[day.strftime("%Y-%m-%d")] = 0

            daily_sales_data = conn.execute(
                "SELECT order_date, SUM(total) FROM orders WHERE order_date >= ? AND status != 'Cancelled' GROUP BY order_date",
                (start_date.strftime("%Y-%m-%d"),)
            ).fetchall()
            for date_str, total in daily_sales_data:
                if date_str in sales_data_dict:
                    sales_data_dict[date_str] = total
        
        sorted_keys = sorted(sales_data_dict.keys())
        labels = [(datetime.strptime(key, "%Y-%m").strftime("%b %Y") if date_range == 'all' else datetime.strptime(key, "%Y-%m-%d").strftime("%b %d")) for key in sorted_keys]
        values = [sales_data_dict[key] for key in sorted_keys]
        sales_chart_data = {"labels": labels, "values": values}
        
        all_statuses = ['Order Received', 'Shipped', 'In Transit', 'Delivered', 'Cancelled']
        status_counts = {status: 0 for status in all_statuses}
        status_distribution_from_db = conn.execute('SELECT status, COUNT(id) FROM orders GROUP BY status').fetchall()
        for status, count in status_distribution_from_db:
            if status in status_counts:
                status_counts[status] = count
        pie_chart_data = {"labels": list(status_counts.keys()), "values": list(status_counts.values())}

        # --- CORRECTED Payment Method Distribution ---
        # 1. Get the total count of ONLY non-cancelled orders
        total_valid_orders = conn.execute(
            "SELECT COUNT(id) FROM orders WHERE status != 'Cancelled'"
        ).fetchone()[0] or 1
        
        # 2. Get the payment method counts for ONLY non-cancelled orders
        payment_data_from_db = conn.execute('''
            SELECT payment_method, COUNT(id) 
            FROM orders 
            WHERE status != 'Cancelled' 
            GROUP BY payment_method
        ''').fetchall()

        # 3. Filter for only the methods we want to display
        valid_methods = ['Cash on Delivery', 'UPI', 'Credit Card', 'Debit Card']
        payment_counts = {method: 0 for method in valid_methods}
        for method, count in payment_data_from_db:
            if method in payment_counts:
                payment_counts[method] = count
        
        # 4. Calculate percentages
        payment_distribution = []
        if total_valid_orders > 0:
            for method, count in payment_counts.items():
                percentage = (count / total_valid_orders) * 100
                payment_distribution.append({
                    "method": method,
                    "percentage": round(percentage, 1)
                })
    
    # Pass all data to the template
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

    with get_db_connection() as conn:
        # --- AOV 12-Month Trend Calculation ---
        aov_by_month = {}
        today = datetime.now()
        for i in range(12):
            current_month = today - timedelta(days=i * 30) # Approximate month steps
            month_key = current_month.strftime('%Y-%m')
            
            month_data = c.execute('''
                SELECT SUM(total), COUNT(id) FROM orders 
                WHERE strftime('%Y-%m', order_date) = ? AND status != 'Cancelled'
            ''', (month_key,)).fetchone()
            
            revenue, orders_count = month_data[0] or 0, month_data[1] or 1
            aov = revenue / orders_count
            aov_by_month[month_key] = aov

        sorted_months = sorted(aov_by_month.keys())
        aov_trend_data = {
            "labels": [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in sorted_months],
            "values": [aov_by_month[m] for m in sorted_months]
        }

    return render_template('admin_aov_report.html', 
                           aov_trend_data=aov_trend_data)

# --- START THE APP ---
if __name__ == '__main__':
    init_db()
    migrate_old_orders()
    threading.Thread(target=update_order_statuses, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)