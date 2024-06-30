# create_tables.py
from initialize_db import get_db_connection

# Function to create the users table
def create_users_table():
    cursor = get_db_connection()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            country TEXT,
            role TEXT,
            permissions TEXT,
            team TEXT,
            profile_picture INTEGER,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.commit()
    cursor.close()
    print("User tables created successfully.")

# Function to create the files table
def create_files_table():
    cursor = get_db_connection()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    cursor.commit()
    cursor.close()
    print("Files table created successfully.")

if __name__ == '__main__':
    create_users_table()
    create_files_table()
    print("Tables creation completed successfully.")

