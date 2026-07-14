from flask import Flask, render_template
from extensions import db, login_manager
from models import User

# Import Blueprints
from routes.auth import auth
from routes.admin import admin
from routes.staff import staff
from routes.user import user

# Initialize Flask application
app = Flask(__name__)

# Basic configuration
app.secret_key = "abc-secret-key"  # Used for session cookies and flash messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and login extensions with Flask app context
db.init_app(app)
login_manager.init_app(app)


# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(staff)
app.register_blueprint(user)


# 1. Main Home / Landing Route
@app.route("/")
def home():
    return render_template("index.html")


# 2. Programmatic Table Creation and Seeding Default Admin on Startup
with app.app_context():
    # Automatically create tables inside site.db if they are not already created
    db.create_all()
    
    # Ensure a pre-existing Admin user exists in the database
    if not User.query.filter_by(username="admin").first():
        admin_user = User(
            username="admin",
            password="admin",
            role="admin",
            is_approved=True,
            is_blacklisted=False
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user ('admin' / 'admin') pre-created programmatically.")

# Run the development server
if __name__ == "__main__":
    app.run(debug=True)