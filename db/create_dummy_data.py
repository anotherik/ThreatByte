# create_dummy_data.py
from initialize_db import get_db_connection
import datetime
import hashlib

# Function to hash passwords using MD5
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Function to insert dummy data into the users table
def insert_dummy_users():
    cursor = get_db_connection()
    users = [
        ('john_doe', 'john@example.com', hash_password('super-secret'), 'USA', 'admin', 'all', 'Team A', datetime.datetime.now(), datetime.datetime.now()),
        ('jane_smith', 'jane@example.com', hash_password('password123'), 'UK', 'user', 'read', 'Team B', datetime.datetime.now(), datetime.datetime.now()),
        ('alice_jones', 'alice@example.com', hash_password('password123'), 'Canada', 'user', 'read', 'Team A', datetime.datetime.now(), datetime.datetime.now()),
        ('bob_brown', 'bob@example.com', hash_password('my-secret'), 'Australia', 'user', 'write', 'Team C', datetime.datetime.now(), datetime.datetime.now()),
        ('carol_white', 'carol@example.com', hash_password('password'), 'Germany', 'user', 'read', 'Team D', datetime.datetime.now(), datetime.datetime.now()),
        ('dave_black', 'dave@example.com', hash_password('password'), 'France', 'admin', 'all', 'Team B', datetime.datetime.now(), datetime.datetime.now()),
        ('eve_green', 'eve@example.com', hash_password('password1'), 'Italy', 'user', 'write', 'Team C', datetime.datetime.now(), datetime.datetime.now()),
        ('frank_yellow', 'frank@example.com', hash_password('password'), 'Spain', 'user', 'read', 'Team D', datetime.datetime.now(), datetime.datetime.now())
    ]
    cursor.executemany('''
        INSERT INTO users (username, email, password, country, role, permissions, team, last_login, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', users)
    cursor.commit()
    cursor.close()
    print("Dummy users inserted successfully.")

if __name__ == '__main__':
    insert_dummy_users()
    print("Dummy data insertion script completed successfully.")

