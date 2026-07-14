import mysql.connector
from mysql.connector import pooling, Error
from flask import current_app

# We define this as a global variable so it persists across requests
mysql_pool = None

def init_db_pool(app):
    """Initializes the MySQL connection pool when the Flask app starts."""
    global mysql_pool
    try:
        # Create a pool of 5 ready-to-use connections.
        mysql_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="goal_metrics_pool",
            pool_size=5,  # 5 connections are held open in memory
            pool_reset_session=True,
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME']
        )
        print("✅ MySQL Connection Pool successfully initialized.")
    except Error as e:
        print(f"❌ Failed to initialize MySQL Pool: {e}")

def get_db_connection():
    """Fetches a connection from the pool for a specific API route to use."""
    global mysql_pool
    if mysql_pool is None:
        raise Exception("Database pool is not initialized.")
    
    try:
        # Borrow a connection from the pool
        return mysql_pool.get_connection()
    except Error as e:
        print(f"Database connection error: {e}")
        return None