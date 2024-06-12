# initialize_db.py
import sqlite3, os
DATABASE_URI = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../db/database.db')

# Function to initialize database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE_URI)
    conn.row_factory = sqlite3.Row  # This allows name-based access to columns
    return conn
