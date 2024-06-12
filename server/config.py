# server/config.py
import os

class Config:
    DEBUG = True
    SESSION_COOKIE_HTTPONLY = False
    SECRET_KEY = "just_another_secret" # application secret
    DATABASE_URI = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../db/database.db')
    UPLOADS_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    PROFILE_PICTURES_UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads/profile_pictures')


