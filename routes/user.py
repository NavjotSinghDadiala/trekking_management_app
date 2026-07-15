from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from extensions import db
from models import User, Trek, Booking

# Define the user Blueprint
user = Blueprint("user", __name__, url_prefix="/user")


# 1. User Dashboard & Trek Browsing Route
@user.route("/dashboard")
def dashboard():
    if not current_user.is_authenticated or current_user.role != "user":
        flash("Unauthorized. Trekker access required.", "danger")
        return redirect(url_for("auth.login"))

    # Fetch filters from request parameters
    search_location = request.args.get("location", "").strip()
    filter_difficulty = request.args.get("difficulty", "").strip()

    # Query open treks by default
    query = Trek.query.filter_by(status="Open")

    # Apply filters programmatically
    if search_location:
        query = query.filter(Trek.location.like(f"%{search_location}%"))
    if filter_difficulty:
        query = query.filter_by(difficulty=filter_difficulty)

    available_treks = query.all()

    # Fetch bookings history for the current user
    my_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()

    return render_template(
        "user_dashboard.html",
        available_treks=available_treks,
        my_bookings=my_bookings,
        search_location=search_location,
        filter_difficulty=filter_difficulty
    )


# 2. Book a Trek
@user.route("/book/<int:trek_id>", methods=["POST"])
def book_trek(trek_id):
    if not current_user.is_authenticated or current_user.role != "user":
        flash("Unauthorized. Trekker access required.", "danger")
        return redirect(url_for("auth.login"))

    trek = Trek.query.get_or_404(trek_id)

    # Validation 1.5: Prevent duplicate trek bookings
    existing_booking = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id, status="Booked").first()
    if existing_booking:
        flash("You have already booked this trek. Duplicate bookings are not allowed.", "warning")
        return redirect(url_for("user.dashboard"))

    # Validation 1: Allow users to book only if trek status is 'Open'
    if trek.status != "Open":
        flash("Sorry, this trek is not open for bookings.", "danger")
        return redirect(url_for("user.dashboard"))

    try:
        num_tickets = int(request.form.get("num_tickets", "1"))
    except ValueError:
        flash("Invalid number of tickets.", "danger")
        return redirect(url_for("user.dashboard"))

    if num_tickets <= 0:
        flash("You must book at least 1 ticket.", "danger")
        return redirect(url_for("user.dashboard"))

    # Validation 2: Prevent overbooking beyond available slots
    if num_tickets > trek.available_slots:
        flash(f"Not enough slots available. Only {trek.available_slots} slots left.", "danger")
        return redirect(url_for("user.dashboard"))

    # Create Booking record
    total_price = trek.price * num_tickets
    new_booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        num_tickets=num_tickets,
        total_price=total_price,
        status="Booked",
        payment_status="Paid"
    )

    # Decrement available slots programmatically
    trek.available_slots -= num_tickets

    db.session.add(new_booking)
    db.session.commit()

    flash(f"Successfully booked {num_tickets} ticket(s) for the '{trek.name}'!", "success")
    return redirect(url_for("user.dashboard"))


# 3. Cancel Booking Route
@user.route("/booking/cancel/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    if not current_user.is_authenticated or current_user.role != "user":
        flash("Unauthorized. Trekker access required.", "danger")
        return redirect(url_for("auth.login"))

    # Secure query: ensure the booking belongs to the current logged-in trekker
    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()

    if booking.status == "Cancelled":
        flash("This booking is already cancelled.", "warning")
        return redirect(url_for("user.dashboard"))

    if booking.status == "Completed":
        flash("Completed bookings cannot be cancelled.", "danger")
        return redirect(url_for("user.dashboard"))

    # Set booking status to Cancelled
    booking.status = "Cancelled"
    
    # Release slots back to the trek
    booking.trek.available_slots += booking.num_tickets

    db.session.commit()
    flash("Your booking has been cancelled and slots have been released.", "success")
    return redirect(url_for("user.dashboard"))


# 4. Edit Profile Route (Simple beginner implementation)
@user.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if not current_user.is_authenticated:
        flash("Please log in first.", "danger")
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        password = request.form.get("password", "").strip()

        if not password or len(password) < 4:
            flash("Password must be at least 4 characters long.", "danger")
            return redirect(url_for("user.edit_profile"))

        # Update current user password
        current_user.password = password
        db.session.commit()
        flash("Profile updated successfully.", "success")
        
        # Redirect based on role
        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        elif current_user.role == "staff":
            return redirect(url_for("staff.dashboard"))
        else:
            return redirect(url_for("user.dashboard"))

    return render_template("user_edit_profile.html")


# 5. Trek Details Route
@user.route("/trek/<int:trek_id>")
def trek_details(trek_id):
    if not current_user.is_authenticated or current_user.role != "user":
        flash("Unauthorized. Trekker access required.", "danger")
        return redirect(url_for("auth.login"))
    
    trek = Trek.query.get_or_404(trek_id)
    return render_template("user_trek_details.html", trek=trek)


# 6. Active Bookings Route
@user.route("/my-bookings")
def my_bookings():
    if not current_user.is_authenticated or current_user.role != "user":
        flash("Unauthorized. Trekker access required.", "danger")
        return redirect(url_for("auth.login"))
    
    bookings = Booking.query.filter_by(user_id=current_user.id, status="Booked").order_by(Booking.booking_date.desc()).all()
    return render_template("user_my_bookings.html", bookings=bookings)


# 7. Trekking History Route
@user.route("/history")
def history():
    if not current_user.is_authenticated or current_user.role != "user":
        flash("Unauthorized. Trekker access required.", "danger")
        return redirect(url_for("auth.login"))
    
    bookings = Booking.query.filter(
        (Booking.user_id == current_user.id) & 
        (Booking.status.in_(["Completed", "Cancelled"]))
    ).order_by(Booking.booking_date.desc()).all()
    return render_template("user_history.html", bookings=bookings)
