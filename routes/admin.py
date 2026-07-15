from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models import User, StaffProfile, Trek, Booking

# Define the admin Blueprint
admin = Blueprint("admin", __name__, url_prefix="/admin")

# Helper function to check if the current user is an admin
def is_admin_user():
    return current_user.is_authenticated and current_user.role == "admin"


# 1. Admin Dashboard Route (Stats, lists, approvals, search)
@admin.route("/dashboard")
@login_required
def dashboard():
    if not is_admin_user():
        flash("Unauthorized. Admin access required.", "danger")
        return redirect(url_for("home"))

    # Stats counters
    trek_count = Trek.query.count()
    user_count = User.query.filter_by(role="user").count()
    staff_count = User.query.filter_by(role="staff").count()
    booking_count = Booking.query.count()

    # Approvals list
    pending_staff = User.query.filter_by(role="staff", is_approved=False).all()
    approved_staff = User.query.filter_by(role="staff", is_approved=True).all()

    # Search Logic
    search_query = request.args.get("search", "").strip()
    search_type = request.args.get("type", "trek").strip()

    search_results = None
    if search_query:
        if search_type == "trek":
            search_results = Trek.query.filter(
                (Trek.name.like(f"%{search_query}%")) | 
                (Trek.location.like(f"%{search_query}%"))
            ).all()
        elif search_type == "staff":
            # Search by username or by StaffProfile name
            search_results = User.query.join(StaffProfile).filter(
                (User.role == "staff") & 
                ((User.username.like(f"%{search_query}%")) | (StaffProfile.name.like(f"%{search_query}%")))
            ).all()
        elif search_type == "user":
            search_results = User.query.filter(
                (User.role == "user") & 
                (User.username.like(f"%{search_query}%"))
            ).all()

    # Standard listings (if no active search)
    all_treks = Trek.query.all()
    all_users = User.query.filter_by(role="user").all()
    all_bookings = Booking.query.all()

    return render_template(
        "admin_dashboard.html",
        trek_count=trek_count,
        user_count=user_count,
        staff_count=staff_count,
        booking_count=booking_count,
        pending_staff=pending_staff,
        approved_staff=approved_staff,
        all_treks=all_treks,
        all_users=all_users,
        all_bookings=all_bookings,
        search_query=search_query,
        search_type=search_type,
        search_results=search_results
    )


# 2. Staff Approval Actions
@admin.route("/staff/approve/<int:staff_id>", methods=["POST"])
@login_required
def approve_staff(staff_id):
    if not is_admin_user():
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    staff = User.query.get_or_404(staff_id)
    if staff.role == "staff":
        staff.is_approved = True
        if staff.staff_profile:
            staff.staff_profile.status = "Active"
        db.session.commit()
        flash(f"Approved guide '{staff.username}' successfully.", "success")
    
    return redirect(url_for("admin.dashboard"))


@admin.route("/staff/reject/<int:staff_id>", methods=["POST"])
@login_required
def reject_staff(staff_id):
    if not is_admin_user():
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    staff = User.query.get_or_404(staff_id)
    username = staff.username
    db.session.delete(staff)
    db.session.commit()
    
    flash(f"Rejected and deleted pending guide request for '{username}'.", "warning")
    return redirect(url_for("admin.dashboard"))


# 3. User & Staff Deactivation / Blacklisting
@admin.route("/user/blacklist/<int:user_id>", methods=["POST"])
@login_required
def blacklist_user(user_id):
    if not is_admin_user():
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    user = User.query.get_or_404(user_id)
    user.is_blacklisted = True
    
    # If the user is staff, update their profile status too
    if user.role == "staff" and user.staff_profile:
        user.staff_profile.status = "Blacklisted"

    db.session.commit()
    flash(f"Successfully blacklisted '{user.username}'.", "warning")
    return redirect(url_for("admin.dashboard"))


@admin.route("/user/unblacklist/<int:user_id>", methods=["POST"])
@login_required
def unblacklist_user(user_id):
    if not is_admin_user():
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    user = User.query.get_or_404(user_id)
    user.is_blacklisted = False
    
    # Reset status if they are staff
    if user.role == "staff" and user.staff_profile:
        user.staff_profile.status = "Active"

    db.session.commit()
    flash(f"Successfully restored '{user.username}'.", "success")
    return redirect(url_for("admin.dashboard"))


# 4. Trek CRUD Operations
@admin.route("/trek/create", methods=["GET", "POST"])
@login_required
def create_trek():
    if not is_admin_user():
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        difficulty = request.form.get("difficulty", "Easy")
        duration = request.form.get("duration", "1").strip()
        max_slots = request.form.get("max_slots", "10").strip()
        assigned_staff_id = request.form.get("assigned_staff_id", "")
        status = request.form.get("status", "Pending")
        start_date_str = request.form.get("start_date", "")
        end_date_str = request.form.get("end_date", "")
        price = request.form.get("price", "0").strip()

        if not name or not location or not start_date_str or not end_date_str:
            flash("All fields are required.", "danger")
            return redirect(url_for("admin.create_trek"))

        # Parse string dates into date objects
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for("admin.create_trek"))

        # Create Trek instance
        staff_id = int(assigned_staff_id) if assigned_staff_id else None
        
        new_trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=int(duration),
            max_slots=int(max_slots),
            available_slots=int(max_slots),  # Starts with full capacity
            assigned_staff_id=staff_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            price=float(price)
        )
        db.session.add(new_trek)
        db.session.commit()
        flash(f"Trek '{name}' has been created successfully.", "success")
        return redirect(url_for("admin.dashboard"))

    # Fetch approved staff list for assignment dropdown
    approved_guides = User.query.filter_by(role="staff", is_approved=True).all()
    return render_template("admin_create_trek.html", approved_guides=approved_guides)


@admin.route("/trek/edit/<int:trek_id>", methods=["GET", "POST"])
@login_required
def edit_trek(trek_id):
    if not is_admin_user():
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        difficulty = request.form.get("difficulty", "Easy")
        duration = request.form.get("duration", "1").strip()
        max_slots = request.form.get("max_slots", "10").strip()
        assigned_staff_id = request.form.get("assigned_staff_id", "")
        status = request.form.get("status", "Pending")
        start_date_str = request.form.get("start_date", "")
        end_date_str = request.form.get("end_date", "")
        price = request.form.get("price", "0").strip()

        if not name or not location or not start_date_str or not end_date_str:
            flash("All fields are required.", "danger")
            return redirect(url_for("admin.edit_trek", trek_id=trek.id))

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for("admin.edit_trek", trek_id=trek.id))

        # Adjust available slots if capacity (max_slots) changes
        new_max = int(max_slots)
        active_bookings_count = Booking.query.filter_by(trek_id=trek.id, status="Booked").count()
        
        # Prevent shrinking capacity below currently booked seats
        if new_max < active_bookings_count:
            flash(f"Cannot shrink slots below current bookings ({active_bookings_count} tickets).", "danger")
            return redirect(url_for("admin.edit_trek", trek_id=trek.id))

        trek.name = name
        trek.location = location
        trek.difficulty = difficulty
        trek.duration = int(duration)
        trek.max_slots = new_max
        trek.available_slots = new_max - active_bookings_count
        trek.assigned_staff_id = int(assigned_staff_id) if assigned_staff_id else None
        trek.status = status
        trek.start_date = start_date
        trek.end_date = end_date
        trek.price = float(price)

        db.session.commit()
        flash("Trek updated successfully.", "success")
        return redirect(url_for("admin.dashboard"))

    approved_guides = User.query.filter_by(role="staff", is_approved=True).all()
    return render_template("admin_edit_trek.html", trek=trek, approved_guides=approved_guides)


@admin.route("/trek/delete/<int:trek_id>", methods=["POST"])
@login_required
def delete_trek(trek_id):
    if not is_admin_user():
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    trek = Trek.query.get_or_404(trek_id)
    name = trek.name
    db.session.delete(trek)
    db.session.commit()
    
    flash(f"Trek '{name}' has been successfully deleted.", "success")
    return redirect(url_for("admin.dashboard"))
