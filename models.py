from datetime import datetime
from extensions import db
from flask_login import UserMixin

# 1. User Model
# Represents all human users: Admins, Trek Staff (guides), and Trekkers (users).
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Plain text for beginner simplicity
    role = db.Column(db.String(20), nullable=False, default="user")  # 'admin', 'staff', 'user'
    
    # Staff status check flags
    is_approved = db.Column(db.Boolean, nullable=False, default=True)  # Staff requires Admin approval
    is_blacklisted = db.Column(db.Boolean, nullable=False, default=False)  # Admin can blacklist users/staff

    # Relationships
    # User <-> Booking (One-to-Many: User makes multiple bookings)
    bookings = db.relationship("Booking", backref="user", lazy=True, cascade="all, delete-orphan")
    
    # Trek Staff <-> Trek (One-to-Many: Staff leads multiple treks)
    assigned_treks = db.relationship("Trek", backref="staff", lazy=True)

    # Link to the detailed profile if they are a Staff member
    # uselist=False creates a One-to-One association with StaffProfile
    staff_profile = db.relationship("StaffProfile", backref="user", uselist=False, cascade="all, delete-orphan")

    # Flask-Login checks is_active. If False, login is blocked.
    # We block login if they are NOT approved OR if they are blacklisted.
    @property
    def is_active(self):
        return self.is_approved and not self.is_blacklisted

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# 2. Staff Profile Model
# Stores detailed contact info and status of a registered staff guide.
class StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    contact_details = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="Pending")  # 'Pending', 'Active', 'Blacklisted'

    def __repr__(self):
        return f"<StaffProfile for {self.name}>"


# 3. Trek Model
# Represents a trekking event (e.g. "Kedar Kantha Trek December 2026")
class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)  # 'Easy', 'Moderate', 'Hard'
    duration = db.Column(db.Integer, nullable=False)  # Duration in days
    
    # Slot details
    max_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    
    # Assigned staff guide (Foreign Key pointing to User.id)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    
    status = db.Column(db.String(50), nullable=False, default="Pending")  # 'Pending', 'Approved', 'Open', 'Closed', 'Completed'
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Relationships
    # Trek <-> Booking (One-to-Many: Trek receives multiple bookings)
    bookings = db.relationship("Booking", backref="trek", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Trek {self.name} - Status: {self.status}>"


# 4. Booking Model
# Represents a trek booked by a user/trekker.
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)
    
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    num_tickets = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Booked")  # 'Booked', 'Cancelled', 'Completed'
    payment_status = db.Column(db.String(50), nullable=False, default="Paid")  # 'Paid', 'Pending'

    def __repr__(self):
        return f"<Booking ID={self.id} UserID={self.user_id} TrekID={self.trek_id}>"
