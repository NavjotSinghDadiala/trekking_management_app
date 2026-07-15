from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from extensions import db, login_manager
from models import User, StaffProfile

# Define the authentication Blueprint
auth = Blueprint("auth", __name__)

# Flask-Login user loader: loads User from database using the session's user ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 1. Login Route
@auth.route("/login", methods=["GET", "POST"])
def login():
    # If already authenticated, redirect to appropriate dashboard
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        elif current_user.role == "staff":
            return redirect(url_for("staff.dashboard"))
        else:
            return redirect(url_for("user.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please fill in both fields.", "danger")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(username=username).first()

        # Validate username and plain-text password
        if user and user.password == password:
            # Check if user is blacklisted
            if user.is_blacklisted:
                flash("Your account has been deactivated/blacklisted by the administrator.", "danger")
                return redirect(url_for("auth.login"))

            # Check if staff guide is approved
            if user.role == "staff" and not user.is_approved:
                flash("Your Guide account is pending approval by the Admin. Please wait.", "warning")
                return redirect(url_for("auth.login"))

            # Log the user in
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")

            # Redirect based on role
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif user.role == "staff":
                return redirect(url_for("staff.dashboard"))
            else:
                return redirect(url_for("user.dashboard"))
        else:
            flash("Invalid username or password. Please try again.", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


# 2. Registration Route
@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        role = request.form.get("role", "user").strip()

        # Extra profile details for staff guides
        contact_details = request.form.get("contact_details", "").strip()

        if not username or not password or not full_name or not email:
            flash("All fields (Username, Full Name, Email, Password) are required.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 4:
            flash("Password must be at least 4 characters long.", "danger")
            return redirect(url_for("auth.register"))

        # Verify username unique constraint
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose another.", "danger")
            return redirect(url_for("auth.register"))

        # Verify email unique constraint
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please choose another.", "danger")
            return redirect(url_for("auth.register"))

        # Set default flags
        is_approved = True
        if role == "staff":
            is_approved = False  # Guides need admin approval

        # Create the User record
        new_user = User(
            username=username,
            password=password,
            role=role,
            email=email,
            full_name=full_name,
            is_approved=is_approved,
            is_blacklisted=False
        )
        db.session.add(new_user)
        db.session.flush()  # Generates new_user.id before committing

        # If registering as a staff guide, create the StaffProfile record
        if role == "staff":
            new_profile = StaffProfile(
                user_id=new_user.id,
                name=full_name,
                contact_details=contact_details or f"Email: {email}",
                status="Pending"
            )
            db.session.add(new_profile)

        db.session.commit()

        if role == "staff":
            flash("Registration successful! Your guide account is pending Admin approval.", "info")
        else:
            flash("Registration successful! You can now log in.", "success")
        
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# 3. Logout Route
@auth.route("/logout")
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for("home"))
    logout_user()
    flash("You have successfully logged out.", "success")
    return redirect(url_for("home"))
