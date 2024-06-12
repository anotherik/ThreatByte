# server/__init__.py

from flask import Flask
from .config import Config

# Create the Flask app object
app = Flask(__name__, template_folder='../client/templates', static_folder='../client/static')

# Load configuration from config.py
app.config.from_object(Config)

# Import route handlers to register routes with the app
from server import routes

# Import API route handlers to register routes with the app
from server.api.v1 import api_v1