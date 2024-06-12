# run.py

from server import app
from server.config import Config

if __name__ == '__main__':
    debug_mode = Config.DEBUG
    app.config['SESSION_COOKIE_NAME'] = 'session_token'
    app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY
    app.run(debug=debug_mode)
