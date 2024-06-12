from flask import render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from server import app
from db.initialize_db import get_db_connection
from .config import Config
import hashlib, os, datetime

UPLOAD_FOLDER = Config.UPLOADS_FOLDER
# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
PROFILE_PICTURES_UPLOAD_FOLDER = Config.PROFILE_PICTURES_UPLOAD_FOLDER
if not os.path.exists(PROFILE_PICTURES_UPLOAD_FOLDER):
    os.makedirs(PROFILE_PICTURES_UPLOAD_FOLDER)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

# Handles user login.
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.

    On GET request:
    Renders the login page.

    On POST request:
    Retrieves the username and password from the login form.
    Queries the database for the user based on the provided username.
    Checks if the provided password matches the hashed password stored in the database.
    If authentication succeeds, stores the username in the session and redirects to the dashboard.
    If authentication fails, renders the login page with an error message.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('login.html', error='Please provide username and password')
        
        # Query the database for the user using parameterized query
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM users WHERE username = ? OR email = ?"
            cursor.execute(query, (username,username))
            user = cursor.fetchone()
        
        # Check if the user exists and the password matches
        if user and user['password'] == custom_hash(password):
            session['username'] = user['username']
            session['user_id'] = user['id']

            # Update last_login timestamp
            cursor.execute("UPDATE users SET last_login = ? WHERE username = ?", (datetime.datetime.now(), username))
            conn.commit()
            conn.close()

            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

# Handles user registration.
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handles user registration.

    On GET request:
    Renders the signup page.

    On POST request:
    Retrieves user registration data from the signup form.
    Performs basic validation checks on the input data.
    Checks if the provided username already exists in the database.
    Inserts the new user into the database.
    Stores the username in the session upon successful registration and redirects to the dashboard.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        country = request.form.get('country')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not country or not password or not confirm_password:
            return render_template('signup.html', error='All fields are required')
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')
                
        # Weak encryption of password (DO NOT USE IN PRODUCTION)
        hashed_password = custom_hash(password)
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                query = "INSERT INTO users (username, email, country, password) VALUES (?, ?, ?, ?)"
                cursor.execute(query, (username, email, country, hashed_password))
                conn.commit()
        except Exception as e:
            print("Error inserting user:", e)  # Print the error message for debugging
            return render_template('signup.html', error='User already exists or database error')
        
        query = "SELECT * FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        session['username'] = user['username']
        session['user_id'] = user['id']

        # Update last_login timestamp
        cursor.execute("UPDATE users SET last_login = ? WHERE username = ?", (datetime.datetime.now(), username))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'username' in session:
        
        search_query = request.args.get('search', '')

        # Get user_id from the session username
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id FROM users WHERE username = ?"
            cursor.execute(query, (session['username'],))
            user = cursor.fetchone()
            user_id = user['id']

        if search_query:
            #cursor.execute("SELECT filename FROM files WHERE user_id = ? AND filename LIKE ?", (user_id, f'%{search_query}%'))
            unsafe_query = f"SELECT filename FROM files WHERE user_id = {user_id} AND filename LIKE '%{search_query}%'"
            cursor.executescript(unsafe_query)
        else:
            cursor.execute("SELECT filename FROM files WHERE user_id = ?", (user_id,))
        files = [row['filename'] for row in cursor.fetchall()]

        # Query files uploaded by this user
        #query = "SELECT filename FROM files WHERE user_id = ?"
        #cursor.execute(query, (user_id,))
        #files = cursor.fetchall()

        return render_template('dashboard.html', files=files, search_query=search_query)
        #return render_template('dashboard.html', files=[file['filename'] for file in files])
    else:
        return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Check if the user is logged in
    if 'username' in session:
        user = get_user_details_from_database(session['user_id'])
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/edit_profile')
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get user_id from the session username
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id FROM users WHERE username = ?"
        cursor.execute(query, (session['username'],))
        user = cursor.fetchone()

    return render_template('edit_profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    # Get current user info
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        current_user = cursor.fetchone()

    # Get form data
    new_username = request.form['username'] or current_user['username']
    email = request.form['email'] or current_user['email']
    country = request.form['country'] or current_user['country']
    if 'role' not in request.form:
        role = current_user['role']
    else:
        role = request.form['role'] or current_user['role']
    #role = request.form['role'] or current_user['role']
    #permissions = request.form['permissions'] or current_user['permissions']
    if 'permissions' not in request.form:
        permissions = current_user['permissions']
    else:
        permissions = request.form['permissions']
    team = request.form['team'] or current_user['team']

    # Handle profile picture upload
    profile_picture_id = current_user['profile_picture']
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file:
            # Generate simple incremental ID for profile picture
            # Get the highest existing ID and increment it by 1
            cursor.execute("SELECT MAX(profile_picture) FROM users")
            max_id = cursor.fetchone()[0]
            if max_id is None:
                max_id = 0
            if max_id:
                profile_picture_id = max_id + 1
            else:
                profile_picture_id = 1
            
            # Save profile picture with simple ID
            filename = str(profile_picture_id) + '.png'
            file.save(os.path.join(PROFILE_PICTURES_UPLOAD_FOLDER, filename))

            #filename = file.filename
            #file.save(os.path.join(PROFILE_PICTURES_UPLOAD_FOLDER, filename))
            #profile_picture = filename
        else:
            profile_picture_id = current_user['profile_picture']

    # Update the user in the database
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                UPDATE users
                SET username = ?, email = ?, country = ?, role = ?, permissions = ?, team = ?, profile_picture = ?
                WHERE username = ?
            """
            cursor.execute(query, (new_username, email, country, role, permissions, team, profile_picture_id, username))
            conn.commit()

        session['username'] = new_username  # Update session username if changed
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    except conn.Error as e:
        print("SQLite error:", e)
        # Rollback the transaction
        conn.rollback()
        flash('Fail to update profile.', 'error')
        return redirect(url_for('edit_profile'))

# Handles file uploads
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Get user_id from the session username
            with get_db_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT id FROM users WHERE username = ?"
                cursor.execute(query, (session['username'],))
                user = cursor.fetchone()
                user_id = user['id']

            # Insert the file into the files table
            cursor.execute("INSERT INTO files (filename, user_id) VALUES (?, ?)", (filename, user_id))
            conn.commit()
            
            flash('File successfully uploaded', 'success')
            return redirect(url_for('dashboard'))
    return render_template('upload.html')

# Route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get user_id from the session username
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id FROM users WHERE username = ?"
        cursor.execute(query, (session['username'],))
        user = cursor.fetchone()
        user_id = user['id']

    # Check if the file belongs to the user
    query = "SELECT * FROM files WHERE filename = ? AND user_id = ?"
    cursor.execute(query, (filename, user_id))
    file = cursor.fetchone()

    if file:
        return send_from_directory(UPLOAD_FOLDER, filename)
    else:
        return "Forbidden", 403

# Route to serve uploaded profile pictures
@app.route('/uploads/profile_pictures/<filename>')
def profile_pictures(filename):
    return send_from_directory(PROFILE_PICTURES_UPLOAD_FOLDER, filename)

# Route to download file
@app.route('/download/<filename>')
def download_file(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    # Query the database for the user ID
    # Get user_id from the session username
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        user_id = user['id']
    
    # Check if the file exists and belongs to the user
    query = "SELECT * FROM files WHERE filename = ? AND user_id = ?"
    cursor.execute(query, (filename, user_id))
    file = cursor.fetchone()
    
    if file:
        return send_from_directory(UPLOAD_FOLDER, filename)
    else:
        flash('You do not have permission to download this file.', 'error')
        return redirect(url_for('dashboard'))

# Route to delete file
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if 'username' not in session:
        return jsonify({'message': 'You are not logged in.', 'type': 'error'})
    
    # Get user_id from the session username
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id FROM users WHERE username = ?"
        cursor.execute(query, (session['username'],))
        user = cursor.fetchone()
        user_id = user['id']
    
    # Check if the file belongs to the user
    query = "SELECT * FROM files WHERE filename = ? AND user_id = ?"
    cursor.execute(query, (filename, user_id))
    file = cursor.fetchone()
    
    if not file:
        return jsonify({'message': 'File not found.', 'type': 'error'})

    # Remove the file from the filesystem and database
    if os.path.exists(file_path):
        os.remove(file_path)
        cursor.execute("DELETE FROM files WHERE filename = ? AND user_id = ?", (filename, user_id))
        conn.commit()
        return jsonify({'message': 'File deleted successfully.', 'type': 'success'})
    else:
        return jsonify({'message': 'File not found on server.', 'type': 'error'})

@app.route('/search')
def search():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    query = request.args.get('query')
    results = []

    # Simulate a search operation (this could be a database query in a real application)
    # For demonstration purposes, just echo the query back as a result
    if query:
        results.append(query)
    
    return render_template('dashboard.html', results=results, query=query)

@app.route('/logout')
def logout():
    # Clear all content from the session cookie
    session.clear()
    return redirect(url_for('login'))

# Weak password hashing function (DO NOT USE IN PRODUCTION)
def custom_hash(password):
    """
    Weak password hashing function using MD5.

    Args:
    - password: The password to hash.

    Returns:
    - The hashed password.
    """
    return hashlib.md5(password.encode()).hexdigest()

# Get user profile from database
def get_user_details_from_database(user_id):
    # Query the database for the user using parameterized query
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
    return user


## API Code
