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
    
    # 1. Drop existing tables to clear old schemas (e.g. the old education/quiz models)
    db.drop_all()
    
    # 2. Create the tables programmatically based on our new models.py definition
    db.create_all()
    print("Database tables created successfully!")

    # 3. Create Seed Data
    print("Seeding initial database content...")

    # A. Users (Admin, Staff, Student)
    admin_user = User(
        username="admin", 
        password="admin", 
        role="admin", 
        is_approved=True
    )
    
    approved_staff = User(
        username="guide1", 
        password="guide1", 
        role="staff", 
        is_approved=True
    )
    
    pending_staff = User(
        username="guide2", 
        password="guide2", 
        role="staff", 
        is_approved=False
    )
    
    trekker_user = User(
        username="trekker1", 
        password="trekker1", 
        role="user", 
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
        name="Kedarkantha Winter Trek",
        location="Uttarakhand",
        difficulty="Moderate",
        duration=6,
        max_slots=20,
        available_slots=20,
        assigned_staff_id=approved_staff.id,
        status="Open",
        start_date=date(2026, 12, 15),
        end_date=date(2026, 12, 21),
        price=8500.0
    )

    trek2 = Trek(
        name="Triund Trail Weekend",
        location="Dharamshala",
        difficulty="Easy",
        duration=2,
        max_slots=15,
        available_slots=15,
        assigned_staff_id=approved_staff.id,
        status="Open",
        start_date=date(2026, 11, 5),
        end_date=date(2026, 11, 7),
        price=2500.0
    )

    trek3 = Trek(
        name="Roopkund Expedition",
        location="Chamoli",
        difficulty="Hard",
        duration=8,
        max_slots=10,
        available_slots=10,
        assigned_staff_id=None,
        status="Pending",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 18),
        price=15000.0
    )

    db.session.add_all([trek1, trek2, trek3])
    db.session.commit()
    print("- Seeded Treks (Kedarkantha - Open, Triund - Open, Roopkund - Pending)")

    print("Database seeding completed successfully!")

if __name__ == "__main__":
    with app.app_context():
        seed_database()
