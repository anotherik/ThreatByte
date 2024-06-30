# server/api/v1/api_v1.py
from flask import request, jsonify, session, abort, make_response
from flask_restx import Api, Resource, fields
from server import app
from server.routes import custom_hash
from db.initialize_db import get_db_connection
import datetime
from functools import wraps
import jwt
from server.config import Config

# Creation of API with Flask-RESTPlus
api = Api(app,
          version='1.0',
          title='ThreatByte API',
          description='API endpoints for the ThreatByte application',
          doc='/api/docs'  # Setting the path for the Swagger documentation
         )

# Define a namespace
ns = api.namespace('api/v1', description='ThreatByte API')

# Model for the login details
login_model = api.model('LoginDetails', {
    'username': fields.String(required=True, description='User\'s username or email'),
    'password': fields.String(required=True, description='User\'s password')
})

# Model for the login response
login_response_model = api.model('LoginResponse', {
    'message': fields.String(description='Response message after successful login'),
    'user': fields.Raw(description='User information returned on successful login'),
    'session_id': fields.String(description='Session ID to be used for subsequent requests')
})

# Model for update profile requests
update_model = api.model('UserProfileUpdate', {
    'user_id': fields.Integer(required=True, description='The user ID to update'),
    'email': fields.String(required=False, description='New email address'),
    'country': fields.String(required=False, description='New country of residence'),
    'team': fields.String(required=False, description='New team assignment'),
    'role': fields.String(required=False, description='User role (sensitive data)'),
    'permissions': fields.String(required=False, description='User permissions (sensitive data)')
})

# Model for the user profile data
user_profile_model = api.model('UserProfile', {
    'username': fields.String(description='User\'s username'),
    'email': fields.String(description='User\'s email address'),
    'country': fields.String(description='User\'s country of residence'),
    'role': fields.String(description='User\'s role'),
    'permissions': fields.String(description='User\'s permissions'),
    'team': fields.String(description='User\'s team')
})

# The model for request arguments
profile_query = ns.parser()
profile_query.add_argument('user_id', type=int, required=True, help='User ID is required', location='args')

# Response model
response_model = api.model('Response', {
    'success': fields.Boolean(description='Success status of the operation'),
    'message': fields.String(description='Response message')
})

# Define the model for error messages (if needed)
error_model = api.model('Error', {
    'message': fields.String(description='A description of the error')
})

# Define the model for successful delete operations
delete_model = api.model('DeleteSuccess', {
    'message': fields.String(description='Confirmation of successful deletion')
})

# Define the model for profile picture update requests
profile_pic_model = api.model('ProfilePicture', {
    'username': fields.String(required=True, description='Username of the user'),
    'picture_url': fields.String(required=True, description='URL to fetch the profile picture from')
})

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Assumes Bearer Token

        if not token:
            return make_response(jsonify({'message': 'Token is missing!'}), 401)

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = data['username']  # You might want to load the user from the database
        except:
            return make_response(jsonify({'message': 'Token is invalid!'}), 401)

        return f(current_user, *args, **kwargs)

    return decorated

@ns.route('/login')
class UserLogin(Resource):
    @ns.expect(login_model)
    @ns.response(200, 'Login successful', login_response_model)
    @ns.response(400, 'Please provide username and password')
    @ns.response(401, 'Invalid username or password')
    @ns.response(405, 'Method not allowed')
    def post(self):
        """
        Handles user login.
        """
        data = request.get_json()  # Get data from request body
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'error': 'Please provide username and password'}, 400
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM users WHERE username = ? OR email = ?"
            cursor.execute(query, (username, username))
            user = cursor.fetchone()

        if user and user['password'] == custom_hash(password):
            
            # Generate JWT
            token = jwt.encode({
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token expires in 24 hours
            }, Config.SECRET_KEY, algorithm='HS256')
            

            # Update last_login timestamp
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET last_login = ? WHERE username = ?", (datetime.datetime.now(), username))
                conn.commit()

            return {'message': 'Login successful', 'token': token}, 200
        else:
            return {'error': 'Invalid username or password'}, 401

@ns.route('/profile')
class UserProfile(Resource):
    @ns.expect(profile_query)
    @ns.response(200, 'Success', user_profile_model)
    @ns.response(400, 'User ID is required')
    @ns.response(404, 'User profile not found')
    #@token_required
    #def get(self, current_user):
    def get(self):
        """
        Retrieves the profile information of a user based on the provided user ID.
        """
        args = profile_query.parse_args()
        user_id = args.get('user_id')

        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT username, email, country, role, permissions, team FROM users WHERE id = ?"
            cursor.execute(query, (user_id,))
            user_profile = cursor.fetchone()

        if user_profile:
            return dict(user_profile), 200
        else:
            return {'error': 'User profile not found'}, 404

@ns.route('/update-profile')
class UserProfileUpdate(Resource):
    @api.expect(update_model)
    @api.response(200, 'Profile updated successfully.', response_model)
    @api.response(401, 'Authentication required.')
    @api.response(403, 'Unauthorized to modify other user profiles.')
    def post(self):
        """
        Updates a user profile information.
        """
        print(session)
        if 'username' in session:
            user_id = session['user_id']
            data = request.json

            if 'user_id' in data and data['user_id'] != user_id:
                abort(403, description="Unauthorized to modify other user profiles.")

            allowed_updates = ['email', 'country', 'team']
            sensitive_updates = ['role', 'permissions']

            updates = {key: value for key, value in data.items() if key in allowed_updates}

            with get_db_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT username, email, country, role, permissions, team FROM users WHERE id = ?"
                cursor.execute(query, (user_id,))
                user_profile = cursor.fetchone()

            if user_profile['role'] == "admin":
                updates.update({key: value for key, value in data.items() if key in sensitive_updates})

            with get_db_connection() as conn:
                cursor = conn.cursor()
                update_query = "UPDATE users SET " + ", ".join([f"{key} = ?" for key in updates.keys()]) + " WHERE id = ?"
                cursor.execute(update_query, list(updates.values()) + [user_id])
                conn.commit()

            return {"success": True, "message": "Profile updated successfully."}, 200
        else:
            abort(401, description="Authentication required.")


@ns.route('/delete-user/<int:user_id>')
@ns.doc(description='Delete a user from the database without proper authorization checks. '
                    'This endpoint represents a Broken Function Level Authorization vulnerability.',
       responses={200: ('User successfully deleted', delete_model),
                  404: ('User not found', error_model)})
class UserDelete(Resource):
    #@token_required
    #def delete(self, current_user, user_id):
    def delete(self, user_id):
        """
            Delete a user from the application.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user:
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                response = make_response(jsonify({'message': 'User deleted successfully'}), 200)
                return response
            else:
                response = make_response(jsonify({'error': 'User not found'}), 404)
                return response

@ns.route('/update_picture')
class ProfilePicture(Resource):
    @api.expect(profile_pic_model)
    def post(self):
        """
        Update the user's profile picture by fetching it from a provided URL.
        This endpoint is vulnerable to SSRF, allowing external service interaction.
        """
        data = api.payload
        username = data['username']
        picture_url = data['picture_url']

        try:
            # Fetch the picture from the URL provided by the user
            response = requests.get(picture_url)

            # Check if the request was successful
            if response.status_code == 200:
                # Here, instead of actually saving the picture, we'll just simulate that process.
                # Vulnerability point: Fetching content from an arbitrary URL provided by the user
                if 'image/jpeg' in response.headers['Content-Type'] or 'image/png' in response.headers['Content-Type']:
                    
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Get the user by username
                    cursor.execute("SELECT id, profile_picture FROM users WHERE username = ?", (username,))
                    current_user = cursor.fetchone()

                    if current_user:
                        user_id = current_user['id']
                        profile_picture_id = current_user['profile_picture']

                        # Generate a new profile picture ID if necessary
                        if profile_picture_id is None:
                            cursor.execute("SELECT MAX(profile_picture) FROM users")
                            max_id = cursor.fetchone()[0]
                            if max_id is None:
                                max_id = 0
                            profile_picture_id = max_id + 1

                        # Save the profile picture file
                        filename = str(profile_picture_id) + '.png'
                        file_path = os.path.join(PROFILE_PICTURES_UPLOAD_FOLDER, filename)
                        with open(file_path, 'wb') as file:
                            file.write(response.content)
                        
                        # Update the user's profile picture ID in the database
                        cursor.execute("UPDATE users SET profile_picture = ? WHERE id = ?", (profile_picture_id, user_id))
                        conn.commit()
                        return {'message': f'Profile picture updated successfully for user {username}'}, 200
                    else:
                        return {'error': 'User not found'}, 404
                else:
                    return {'error': 'Invalid image format'}, 400
            else:
                return {'message': 'Failed to fetch the picture from the provided URL'}, 400
        except Exception as e:
            return {'message': str(e)}, 500
