from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from extensions import db
from models import User, Trek, Booking

# Define the staff Blueprint
staff = Blueprint("staff", __name__, url_prefix="/staff")


# 1. Staff Dashboard Route
@staff.route("/dashboard")
def dashboard():
    if not current_user.is_authenticated or current_user.role != "staff" or not current_user.is_approved:
        flash("Unauthorized. Approved Staff access required.", "danger")
        return redirect(url_for("auth.login"))

    # Fetch treks assigned to this specific staff member
    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    
    # Calculate registered users count for each trek
    trek_stats = []
    for trek in assigned_treks:
        bookings_count = Booking.query.filter_by(trek_id=trek.id, status="Booked").count()
        trek_stats.append({
            "trek": trek,
            "bookings_count": bookings_count
        })

    return render_template("staff_dashboard.html", treks_data=trek_stats)


# 2. View and Manage Trek Details (slots, status, participant list)
@staff.route("/trek/manage/<int:trek_id>", methods=["GET"])
def manage_trek(trek_id):
    if not current_user.is_authenticated or current_user.role != "staff" or not current_user.is_approved:
        flash("Unauthorized. Approved Staff access required.", "danger")
        return redirect(url_for("auth.login"))

    trek = Trek.query.get_or_404(trek_id)

    # Core Security Requirement: Ensure only assigned staff can manage a trek
    if trek.assigned_staff_id != current_user.id:
        flash("Access Denied. You are not assigned to lead this trek.", "danger")
        return redirect(url_for("staff.dashboard"))

    # Fetch all active bookings for this trek to show the participant list
    active_bookings = Booking.query.filter_by(trek_id=trek.id, status="Booked").all()

    return render_template("staff_manage_trek.html", trek=trek, bookings=active_bookings)


# 3. Update Trek Slots
@staff.route("/trek/update_slots/<int:trek_id>", methods=["POST"])
def update_slots(trek_id):
    if not current_user.is_authenticated or current_user.role != "staff" or not current_user.is_approved:
        flash("Unauthorized. Approved Staff access required.", "danger")
        return redirect(url_for("auth.login"))

    trek = Trek.query.get_or_404(trek_id)

    # Core Security: Ensure only assigned staff can manage a trek
    if trek.assigned_staff_id != current_user.id:
        flash("Access Denied. You are not assigned to lead this trek.", "danger")
        return redirect(url_for("staff.dashboard"))

    try:
        new_slots = int(request.form.get("available_slots", "0"))
    except ValueError:
        flash("Please enter a valid integer for available slots.", "danger")
        return redirect(url_for("staff.manage_trek", trek_id=trek.id))

    active_bookings_count = Booking.query.filter_by(trek_id=trek.id, status="Booked").count()

    # Simple validations
    if new_slots < 0:
        flash("Available slots cannot be negative.", "danger")
    elif active_bookings_count + new_slots > trek.max_slots:
        flash(f"Total capacity exceeded. The maximum slots for this trek is {trek.max_slots}. Currently booked: {active_bookings_count}.", "danger")
    else:
        trek.available_slots = new_slots
        db.session.commit()
        flash("Available slots updated successfully.", "success")

    return redirect(url_for("staff.manage_trek", trek_id=trek.id))


# 4. Update Trek Status (Open/Closed/Ongoing/Completed)
@staff.route("/trek/update_status/<int:trek_id>", methods=["POST"])
def update_status(trek_id):
    if not current_user.is_authenticated or current_user.role != "staff" or not current_user.is_approved:
        flash("Unauthorized. Approved Staff access required.", "danger")
        return redirect(url_for("auth.login"))

    trek = Trek.query.get_or_404(trek_id)

    # Core Security: Ensure only assigned staff can manage a trek
    if trek.assigned_staff_id != current_user.id:
        flash("Access Denied. You are not assigned to lead this trek.", "danger")
        return redirect(url_for("staff.dashboard"))

    new_status = request.form.get("status", "").strip()
    valid_statuses = ["Open", "Completed"]

    if new_status in valid_statuses:
        trek.status = new_status
        
        # If the trek is marked as Completed, update all associated bookings from Booked to Completed
        if new_status == "Completed":
            active_bookings = Booking.query.filter_by(trek_id=trek.id, status="Booked").all()
            for booking in active_bookings:
                booking.status = "Completed"
                
        db.session.commit()
        flash(f"Trek status updated to '{new_status}' successfully.", "success")
    else:
        flash("Invalid status selection.", "danger")

    return redirect(url_for("staff.manage_trek", trek_id=trek.id))
