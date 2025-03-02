from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime, timedelta
import mysql.connector
import json
import random
import traceback
from functools import wraps
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# User login required decorator
def user_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin login required decorator
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2002',  
    'database': 'restaurant_db'
}

def init_db():
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS restaurant_db")
        cursor.execute("USE restaurant_db")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(15),
                password VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
        """)
        
        # Create departments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                dept_id INT AUTO_INCREMENT PRIMARY KEY,
                dept_name VARCHAR(50) NOT NULL,
                location VARCHAR(100)
            ) ENGINE=InnoDB
        """)
        
        # Create employees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                emp_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE,
                phone VARCHAR(15),
                hire_date DATE,
                salary DECIMAL(10, 2),
                dept_id INT,
                FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
            ) ENGINE=InnoDB
        """)
        
        # Create customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE,
                phone VARCHAR(15),
                address TEXT
            ) ENGINE=InnoDB
        """)
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                customer_id INT,
                emp_id INT,
                total_amount DECIMAL(10, 2),
                status VARCHAR(50) DEFAULT 'Pending',
                payment_method VARCHAR(50),
                delivery_address TEXT,
                special_instructions TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
            ) ENGINE=InnoDB
        """)
        
        # Create order_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                item_id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT,
                item_name VARCHAR(100),
                quantity INT,
                price DECIMAL(10, 2),
                special_requests TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            ) ENGINE=InnoDB
        """)
        
        # Insert sample data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM departments")
        if cursor.fetchone()[0] == 0:
            # Insert departments
            cursor.executemany(
                "INSERT INTO departments (dept_name, location) VALUES (%s, %s)",
                [
                    ("Kitchen", "Ground Floor"),
                    ("Service", "Ground Floor"),
                    ("Management", "First Floor")
                ]
            )
            
            # Insert employees
            cursor.executemany(
                """INSERT INTO employees 
                   (first_name, last_name, email, phone, hire_date, salary, dept_id) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                [
                    ("John", "Doe", "john@email.com", "1234567890", "2024-01-01", 50000, 1),
                    ("Jane", "Smith", "jane@email.com", "0987654321", "2024-01-15", 45000, 2),
                    ("Mike", "Johnson", "mike@email.com", "5555555555", "2024-02-01", 60000, 3)
                ]
            )
            
            # Insert customers
            cursor.executemany(
                "INSERT INTO customers (name, email, phone, address) VALUES (%s, %s, %s, %s)",
                [
                    ("Alice Brown", "alice@email.com", "1112223333", "123 Main St"),
                    ("Bob Wilson", "bob@email.com", "4445556666", "456 Oak Ave"),
                    ("Carol White", "carol@email.com", "7778889999", "789 Pine Rd")
                ]
            )
            
            # Insert orders
            orders_data = [
                (1, 2, 45.99, 'Completed', 'Credit Card', '123 Main St'),
                (2, 2, 32.50, 'In Progress', 'Cash', '456 Oak Ave'),
                (3, 2, 28.75, 'Pending', 'Credit Card', '789 Pine Rd')
            ]
            cursor.executemany(
                """INSERT INTO orders 
                   (customer_id, emp_id, total_amount, status, payment_method, delivery_address)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                orders_data
            )
            
            # Insert order items
            items_data = [
                (1, 'Vegetable Spring Rolls', 2, 8.99),
                (1, 'Paneer Butter Masala', 1, 14.99),
                (2, 'Green Salad', 1, 7.50),
                (2, 'Mushroom Risotto', 1, 16.99),
                (3, 'Vegetable Biryani', 2, 12.99)
            ]
            cursor.executemany(
                "INSERT INTO order_items (order_id, item_name, quantity, price) VALUES (%s, %s, %s, %s)",
                items_data
            )
            
        conn.commit()
        print("Database initialized successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Initialize database
init_db()

# Load menu data with web image URLs
MENU_DATA = {
    "starters": [
        {"id": 1, "name": "Vegetable Spring Rolls", "price": 8.99, "image": "https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=400"},
        {"id": 2, "name": "Garden Fresh Salad", "price": 7.99, "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400"},
        {"id": 3, "name": "Crispy Corn", "price": 6.99, "image": "https://images.pexels.com/photos/603030/pexels-photo-603030.jpeg?auto=compress&cs=tinysrgb&w=400"},
        {"id": 4, "name": "Mushroom Soup", "price": 5.99, "image": "https://images.pexels.com/photos/539451/pexels-photo-539451.jpeg?auto=compress&cs=tinysrgb&w=400"},
        {"id": 5, "name": "Paneer Tikka", "price": 9.99, "image": "https://images.pexels.com/photos/9609838/pexels-photo-9609838.jpeg?auto=compress&cs=tinysrgb&w=400"}
    ],
    "mains": [
        {"id": 6, "name": "Paneer Butter Masala", "price": 14.99, "image": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400"},
        {"id": 7, "name": "Vegetable Biryani", "price": 13.99, "image": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=400"},
        {"id": 8, "name": "Dal Makhani", "price": 12.99, "image": "https://images.pexels.com/photos/2474661/pexels-photo-2474661.jpeg?auto=compress&cs=tinysrgb&w=400"},
        {"id": 9, "name": "Veg Pasta Arrabiata", "price": 11.99, "image": "https://images.pexels.com/photos/1437267/pexels-photo-1437267.jpeg?auto=compress&cs=tinysrgb&w=400"},
        {"id": 10, "name": "Buddha Bowl", "price": 13.99, "image": "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=400"},
        {"id": 11, "name": "Mushroom Risotto", "price": 15.99, "image": "https://images.pexels.com/photos/6287500/pexels-photo-6287500.jpeg?auto=compress&cs=tinysrgb&w=400"}
    ],
    "desserts": [
        {"id": 12, "name": "Gulab Jamun", "price": 5.99, "image": "https://images.pexels.com/photos/14705134/pexels-photo-14705134.jpeg?auto=compress&cs=tinysrgb&w=400"},
        {"id": 13, "name": "Mango Ice Cream", "price": 4.99, "image": "https://images.unsplash.com/photo-1560008581-09826d1de69e?w=400"},
        {"id": 14, "name": "Chocolate Brownie", "price": 6.99, "image": "https://images.pexels.com/photos/2067396/pexels-photo-2067396.jpeg?auto=compress&cs=tinysrgb&w=400"},
        {"id": 15, "name": "Fruit Tart", "price": 5.99, "image": "https://images.pexels.com/photos/2693447/pexels-photo-2693447.jpeg?auto=compress&cs=tinysrgb&w=400"},
        {"id": 16, "name": "Carrot Cake", "price": 6.99, "image": "https://images.pexels.com/photos/4110541/pexels-photo-4110541.jpeg?auto=compress&cs=tinysrgb&w=400"}
    ]
}

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/')
def index():
    return render_template('index.html', menu=MENU_DATA)

@app.route('/dashboard')
@admin_login_required
def dashboard():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Get current date
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Get dashboard statistics
        cursor.execute("""
            SELECT COUNT(*) as orders_today, COALESCE(SUM(total_amount), 0) as revenue_today 
            FROM orders 
            WHERE DATE(order_date) = CURDATE()
        """)
        daily_stats = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as active_orders FROM orders WHERE status != 'Completed'")
        active_orders = cursor.fetchone()['active_orders']
        
        cursor.execute("SELECT COUNT(*) as total_customers FROM customers")
        total_customers = cursor.fetchone()['total_customers']
        
        # Get weekly revenue data
        cursor.execute("""
            SELECT DATE(order_date) as date, COALESCE(SUM(total_amount), 0) as revenue
            FROM orders
            WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(order_date)
            ORDER BY date
        """)
        weekly_revenue = cursor.fetchall()
        
        # Get popular items
        cursor.execute("""
            SELECT item_name, COUNT(*) as count
            FROM order_items
            GROUP BY item_name
            ORDER BY count DESC
            LIMIT 5
        """)
        popular_items = cursor.fetchall()
        
        # Get recent orders with customer names
        cursor.execute("""
            SELECT o.*, c.name as customer_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            ORDER BY order_date DESC
            LIMIT 10
        """)
        orders = cursor.fetchall()
        
        # Get order items for each order
        for order in orders:
            cursor.execute("""
                SELECT * FROM order_items
                WHERE order_id = %s
            """, (order['order_id'],))
            order['items'] = cursor.fetchall()
        
        # Get employees with order counts
        cursor.execute("""
            SELECT e.*, d.dept_name,
                   COUNT(o.order_id) as orders_handled
            FROM employees e
            LEFT JOIN departments d ON e.dept_id = d.dept_id
            LEFT JOIN orders o ON e.emp_id = o.emp_id
            GROUP BY e.emp_id, e.first_name, e.last_name, e.email, e.phone, e.hire_date, e.salary, d.dept_name
        """)
        employees = cursor.fetchall()
        
        # Get customers with order statistics
        cursor.execute("""
            SELECT c.*,
                   COUNT(o.order_id) as total_orders,
                   COALESCE(SUM(o.total_amount), 0) as total_spent
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.name, c.email, c.phone, c.address
        """)
        customers = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        stats = {
            'orders_today': daily_stats['orders_today'],
            'revenue_today': daily_stats['revenue_today'],
            'active_orders': active_orders,
            'total_customers': total_customers
        }
        
        return render_template('dashboard.html',
                             current_date=current_date,
                             stats=stats,
                             weekly_revenue=json.dumps([float(row['revenue']) for row in weekly_revenue]),
                             popular_items=json.dumps([{'name': row['item_name'], 'count': row['count']} for row in popular_items]),
                             orders=orders,
                             employees=employees,
                             customers=customers)
                             
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return "Database error occurred. Please check server logs.", 500
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred.", 500

@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400
        
    conn = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE orders
            SET status = ?
            WHERE order_id = ?
        """, (new_status, order_id))
        conn.commit()
        
        return jsonify({'message': 'Order status updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT o.*, 
                   c.name as customer_name,
                   CONCAT(e.first_name, ' ', e.last_name) as employee_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN employees e ON o.emp_id = e.emp_id
            ORDER BY o.order_date DESC
        """)
        
        orders = cursor.fetchall()
        
        # Get items for each order
        for order in orders:
            cursor.execute("""
                SELECT * FROM order_items 
                WHERE order_id = ?
            """, (order['order_id'],))
            order['items'] = cursor.fetchall()
        
        return jsonify(orders)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/place-order', methods=['POST'])
def place_order():
    try:
        order_data = request.json
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = conn.cursor()
        
        # Get or create customer
        customer_data = order_data.get('customer', {})
        if customer_data.get('email'):
            cursor.execute("SELECT customer_id FROM customers WHERE email = ?", (customer_data['email'],))
            result = cursor.fetchone()
            if result:
                customer_id = result[0]
            else:
                cursor.execute("""
                    INSERT INTO customers (name, email, phone, address)
                    VALUES (%s, %s, %s, %s)
                """, (
                    customer_data.get('name', 'Guest'),
                    customer_data['email'],
                    customer_data.get('phone', ''),
                    customer_data.get('address', '')
                ))
                customer_id = cursor.lastrowid
        else:
            customer_id = 1  # Default guest customer
        
        # Insert order
        order_query = """
            INSERT INTO orders (
                order_date, customer_id, emp_id, total_amount, status,
                payment_method, delivery_address, special_instructions
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        order_values = (
            datetime.now(),
            customer_id,
            order_data.get('emp_id', 1),
            order_data['total'],
            'Pending',
            order_data.get('payment_method', 'Credit Card'),
            order_data.get('delivery_address', ''),
            order_data.get('special_instructions', '')
        )
        cursor.execute(order_query, order_values)
        order_id = cursor.lastrowid
        
        # Insert order items
        item_query = """
            INSERT INTO order_items (
                order_id, item_name, quantity, price, special_requests
            )
            VALUES (%s, %s, %s, %s, %s)
        """
        for item in order_data['items']:
            item_values = (
                order_id,
                item['name'],
                item['quantity'],
                item['price'],
                item.get('special_requests', '')
            )
            cursor.execute(item_query, item_values)
        
        conn.commit()
        return jsonify({
            "message": "Order placed successfully!",
            "order_id": order_id,
            "order": order_data
        })
        
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to home
    if session.get('user_logged_in'):
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return render_template('login.html', error='Please fill in all fields')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Hash the password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Check user credentials
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user and user['password'] == hashed_password:
                session['user_logged_in'] = True
                session['user_id'] = user['user_id']
                session['user_name'] = user['name']
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='Invalid email or password')
                
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return render_template('login.html', error='An error occurred. Please try again.')
            
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Check if email already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return render_template('signup.html', error='Email already registered')
            
            # Hash the password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Insert new user
            cursor.execute("""
                INSERT INTO users (name, email, phone, password)
                VALUES (%s, %s, %s, %s)
            """, (name, email, phone, hashed_password))
            
            conn.commit()
            
            # Log the user in
            session['user_logged_in'] = True
            session['user_id'] = cursor.lastrowid
            session['user_name'] = name
            
            flash('Account created successfully!', 'success')
            return redirect(url_for('index'))
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return render_template('signup.html', error='An error occurred. Please try again.')
            
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile')
@user_login_required
def profile():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Get user details
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        # Get user's orders
        cursor.execute("""
            SELECT o.*, GROUP_CONCAT(oi.item_name) as items
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.customer_id = %s
            GROUP BY o.order_id
            ORDER BY o.order_date DESC
        """, (session['user_id'],))
        orders = cursor.fetchall()
        
        return render_template('profile.html', user=user, orders=orders)
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        flash('An error occurred while loading your profile', 'error')
        return redirect(url_for('index'))
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/edit_profile', methods=['GET', 'POST'])
@user_login_required
def edit_profile():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            
            # Get current user data
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
            user = cursor.fetchone()
            
            # Verify current password if trying to change password
            if current_password:
                hashed_current = hashlib.sha256(current_password.encode()).hexdigest()
                if hashed_current != user['password']:
                    return render_template('edit_profile.html', user=user, error='Current password is incorrect')
            
            # Check if email is already taken by another user
            if email != user['email']:
                cursor.execute("SELECT * FROM users WHERE email = %s AND user_id != %s", (email, session['user_id']))
                if cursor.fetchone():
                    return render_template('edit_profile.html', user=user, error='Email is already taken')
            
            # Update user information
            if new_password:
                hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                cursor.execute("""
                    UPDATE users 
                    SET name = %s, email = %s, phone = %s, password = %s
                    WHERE user_id = %s
                """, (name, email, phone, hashed_password, session['user_id']))
            else:
                cursor.execute("""
                    UPDATE users 
                    SET name = %s, email = %s, phone = %s
                    WHERE user_id = %s
                """, (name, email, phone, session['user_id']))
            
            conn.commit()
            session['user_name'] = name  # Update session name
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        
        # GET request - show edit form
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
        user = cursor.fetchone()
        return render_template('edit_profile.html', user=user)
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        flash('An error occurred while updating your profile', 'error')
        return redirect(url_for('profile'))
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
