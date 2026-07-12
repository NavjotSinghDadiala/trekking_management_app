import os
from flask import Flask
from extensions import db
from models import User, Subject, Chapter, Quiz, Question, Score

# Create a temporary Flask app context to run SQLAlchemy creation commands
app = Flask(__name__)

# Use the exact site.db database file in the project folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the db extension with our temporary app
db.init_app(app)

def seed_database():
    print("Initializing programmatic database creation inside site.db...")
    
    # 1. Drop existing tables to clear old schemas (e.g. the old Trekking models or basic User model)
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
        username="teacher", 
        password="teacher", 
        role="staff", 
        is_approved=True
    )
    
    pending_staff = User(
        username="guide", 
        password="guide", 
        role="staff", 
        is_approved=False
    )
    
    student_user = User(
        username="student", 
        password="student", 
        role="user", 
        is_approved=True
    )

    db.session.add_all([admin_user, approved_staff, pending_staff, student_user])
    db.session.commit()
    print("- Seeded Users (Admin: 'admin', Staff: 'teacher' & 'guide', Student: 'student')")

    # B. Subjects
    maths = Subject(
        name="Mathematics", 
        description="Study of numbers, shapes, and patterns."
    )
    science = Subject(
        name="Science", 
        description="Exploring the physical and natural world through observation."
    )
    
    db.session.add_all([maths, science])
    db.session.commit()
    print("- Seeded Subjects (Mathematics, Science)")

    # C. Chapters
    algebra = Chapter(
        subject_id=maths.id, 
        name="Algebra", 
        description="Introduction to variables, equations, and expressions."
    )
    gravity = Chapter(
        subject_id=science.id, 
        name="Gravity & Motion", 
        description="Understanding force, speed, and gravitational acceleration."
    )

    db.session.add_all([algebra, gravity])
    db.session.commit()
    print("- Seeded Chapters (Algebra, Gravity & Motion)")

    # D. Quizzes
    quiz_algebra = Quiz(
        chapter_id=algebra.id, 
        title="Algebra Basics Quiz", 
        time_duration=10, 
        is_published=True
    )
    quiz_gravity = Quiz(
        chapter_id=gravity.id, 
        title="Gravity Basics Quiz", 
        time_duration=5, 
        is_published=True
    )

    db.session.add_all([quiz_algebra, quiz_gravity])
    db.session.commit()
    print("- Seeded Quizzes (Algebra Basics Quiz, Gravity Basics Quiz)")

    # E. Questions
    q1 = Question(
        quiz_id=quiz_algebra.id,
        question_text="What is the value of x in the equation: 2x + 5 = 15?",
        option_a="5",
        option_b="10",
        option_c="15",
        option_d="20",
        correct_option="A",
        marks=2
    )

    q2 = Question(
        quiz_id=quiz_algebra.id,
        question_text="If 3x = 9, what is the value of x?",
        option_a="1",
        option_b="2",
        option_c="3",
        option_d="4",
        correct_option="C",
        marks=1
    )

    q3 = Question(
        quiz_id=quiz_gravity.id,
        question_text="What is the approximate acceleration due to gravity on Earth's surface?",
        option_a="9.8 m/s^2",
        option_b="5.5 m/s^2",
        option_c="12.0 m/s^2",
        option_d="1.6 m/s^2",
        correct_option="A",
        marks=2
    )

    db.session.add_all([q1, q2, q3])
    db.session.commit()
    print("- Seeded Questions for both quizzes")
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    with app.app_context():
        seed_database()
