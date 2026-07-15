import os
from datetime import datetime, date
from flask import Flask
from extensions import db
from models import User, StaffProfile, Trek, Booking

# Create a temporary Flask app context to run SQLAlchemy creation commands
app = Flask(__name__)

# Use the exact site.db database file in the project folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the db extension with our temporary app
db.init_app(app)

def seed_database():
    print("Initializing programmatic database creation inside site.db...")
    
    # 1. Drop existing tables to clear old schemas
    db.drop_all()
    
    # 2. Create the tables programmatically based on our updated models.py definition
    db.create_all()
    print("Database tables created successfully!")

    # 3. Create Seed Data
    print("Seeding initial database content...")

    # A. Users (Admin, Staff, Trekker)
    admin_user = User(
        username="admin", 
        password="admin", 
        role="admin", 
        email="admin@trekking.com",
        full_name="System Admin",
        is_approved=True
    )
    
    approved_staff = User(
        username="guide1", 
        password="guide1", 
        role="staff", 
        email="rohan@trekking.com",
        full_name="Rohan Sharma",
        is_approved=True
    )
    
    pending_staff = User(
        username="guide2", 
        password="guide2", 
        role="staff", 
        email="aarav@trekking.com",
        full_name="Aarav Patel",
        is_approved=False
    )
    
    trekker_user = User(
        username="trekker1", 
        password="trekker1", 
        role="user", 
        email="amit@trekking.com",
        full_name="Amit Sharma",
        is_approved=True
    )

    db.session.add_all([admin_user, approved_staff, pending_staff, trekker_user])
    db.session.commit()
    print("- Seeded Users (Admin: 'admin', Staff: 'guide1' & 'guide2', Trekker: 'trekker1')")

    # B. Staff Profiles (Linked to the staff Users)
    profile1 = StaffProfile(
        user_id=approved_staff.id,
        name="Rohan Sharma",
        contact_details="Email: rohan@trekking.com, Phone: +91-9876543210",
        status="Active"
    )

    profile2 = StaffProfile(
        user_id=pending_staff.id,
        name="Aarav Patel",
        contact_details="Email: aarav@trekking.com, Phone: +91-9876543211",
        status="Pending"
    )

    db.session.add_all([profile1, profile2])
    db.session.commit()
    print("- Seeded Staff Profiles (Rohan Sharma - Active, Aarav Patel - Pending)")

    # C. Treks
    trek1 = Trek(
        name="Everest Base Camp",
        location="Nepal",
        difficulty="Hard",
        duration=12,
        description="A challenging walk of a lifetime to the base of the world's highest peak, Everest, passing through Sherpa villages and monasteries.",
        max_slots=20,
        available_slots=20,
        assigned_staff_id=approved_staff.id,
        status="Open",
        start_date=date(2026, 5, 20),
        end_date=date(2026, 5, 31),
        price=85000.0
    )

    trek2 = Trek(
        name="Roopkund Trek",
        location="Uttarakhand",
        difficulty="Moderate",
        duration=15,
        description="Famous for the high altitude Roopkund Lake where ancient human skeletons are scattered along the shore, set in Alpine meadows.",
        max_slots=15,
        available_slots=15,
        assigned_staff_id=approved_staff.id,
        status="Open",
        start_date=date(2026, 6, 10),
        end_date=date(2026, 6, 25),
        price=15000.0
    )

    trek3 = Trek(
        name="Hampata Pass",
        location="Himachal",
        difficulty="Moderate",
        duration=12,
        description="A breathtaking pass crossing from the green valleys of Kullu to the stark, dry high-altitude desert of Spiti Valley.",
        max_slots=20,
        available_slots=20,
        assigned_staff_id=None,
        status="Open",
        start_date=date(2026, 7, 10),
        end_date=date(2026, 7, 22),
        price=9500.0
    )

    db.session.add_all([trek1, trek2, trek3])
    db.session.commit()
    print("- Seeded Treks (Everest Base Camp - Open, Roopkund - Open, Hampata Pass - Open)")

    # D. Seed a sample booking to match recent bookings wireframe stats
    booking1 = Booking(
        user_id=trekker_user.id,
        trek_id=trek1.id,
        num_tickets=1,
        total_price=85000.0,
        status="Booked",
        payment_status="Paid"
    )
    # Deduct slot
    trek1.available_slots -= 1
    
    db.session.add(booking1)
    db.session.commit()
    print("- Seeded Bookings (Amit Sharma booked Everest Base Camp)")

    print("Database seeding completed successfully!")

if __name__ == "__main__":
    with app.app_context():
        seed_database()
