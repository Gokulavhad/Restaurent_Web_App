import mysql.connector
from datetime import datetime

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2002',  # Updated password
}

def init_db():
    try:
        # Connect without database first
        print("Connecting to MySQL...")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Create and use database
        print("Creating database...")
        cursor.execute("DROP DATABASE IF EXISTS restaurant_db")
        cursor.execute("CREATE DATABASE restaurant_db")
        cursor.execute("USE restaurant_db")
        print("Database created and selected!")
        
        # Create tables
        print("Creating tables...")
        
        # Departments table
        cursor.execute("""
            CREATE TABLE departments (
                dept_id INT AUTO_INCREMENT PRIMARY KEY,
                dept_name VARCHAR(50) NOT NULL,
                location VARCHAR(100)
            )
        """)
        print("Departments table created!")
        
        # Employees table
        cursor.execute("""
            CREATE TABLE employees (
                emp_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(15),
                hire_date DATE,
                salary DECIMAL(10, 2),
                dept_id INT,
                FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
            )
        """)
        print("Employees table created!")
        
        # Customers table
        cursor.execute("""
            CREATE TABLE customers (
                customer_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(15),
                address TEXT
            )
        """)
        print("Customers table created!")
        
        # Orders table
        cursor.execute("""
            CREATE TABLE orders (
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
            )
        """)
        print("Orders table created!")
        
        # Order items table
        cursor.execute("""
            CREATE TABLE order_items (
                item_id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT,
                item_name VARCHAR(100),
                quantity INT,
                price DECIMAL(10, 2),
                special_requests TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            )
        """)
        print("Order items table created!")
        
        # Insert sample data
        print("Inserting sample data...")
        
        # Insert departments
        departments_data = [
            ("Kitchen", "Ground Floor"),
            ("Service", "Ground Floor"),
            ("Management", "First Floor")
        ]
        cursor.executemany("INSERT INTO departments (dept_name, location) VALUES (%s, %s)", departments_data)
        print("Departments data inserted!")
        
        # Insert employees
        employees_data = [
            ("John", "Doe", "john@email.com", "1234567890", "2024-01-01", 50000, 1),
            ("Jane", "Smith", "jane@email.com", "0987654321", "2024-01-15", 45000, 2),
            ("Mike", "Johnson", "mike@email.com", "5555555555", "2024-02-01", 60000, 3)
        ]
        cursor.executemany(
            """INSERT INTO employees 
            (first_name, last_name, email, phone, hire_date, salary, dept_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
            employees_data
        )
        print("Employees data inserted!")
        
        # Insert customers
        customers_data = [
            ("Alice Brown", "alice@email.com", "1112223333", "123 Main St"),
            ("Bob Wilson", "bob@email.com", "4445556666", "456 Oak Ave"),
            ("Carol White", "carol@email.com", "7778889999", "789 Pine Rd")
        ]
        cursor.executemany(
            "INSERT INTO customers (name, email, phone, address) VALUES (%s, %s, %s, %s)",
            customers_data
        )
        print("Customers data inserted!")
        
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
        print("Orders data inserted!")
        
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
        print("Order items data inserted!")
        
        # Commit changes
        conn.commit()
        print("All changes committed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    init_db()
