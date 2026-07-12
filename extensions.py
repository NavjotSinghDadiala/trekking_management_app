from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize SQLAlchemy ORM. This object will be used to define models and query the database.
db = SQLAlchemy()

# Initialize Flask-Login's LoginManager. This handles user session management, logging in, logging out, and tracking current_user.
login_manager = LoginManager()

# We can specify the login view that Flask-Login redirects users to if they try to access a protected page.
login_manager.login_view = "auth.login"

# Customize the flash message category for better styling with Bootstrap (e.g., 'warning' or 'danger')
login_manager.login_message_category = "warning"
