from datetime import datetime
from extensions import db
from flask_login import UserMixin

# 1. User Model
# Represents Students, Teachers (Staff), and Administrators.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Plain text for beginner simplicity
    role = db.Column(db.String(20), nullable=False, default="user")  # 'admin', 'staff', 'user'
    is_approved = db.Column(db.Boolean, nullable=False, default=True)  # Staff requires Admin approval

    # Relationships
    scores = db.relationship("Score", backref="user", lazy=True, cascade="all, delete-orphan")

    @property
    def is_active(self):
        # Unapproved staff cannot log in
        return self.is_approved

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# 2. Subject Model
# Represents a subject category (e.g., Mathematics, Science).
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # A subject has multiple chapters
    chapters = db.relationship("Chapter", backref="subject", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subject {self.name}>"


# 3. Chapter Model
# Represents a chapter/topic under a specific subject.
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # A chapter has multiple quizzes
    quizzes = db.relationship("Quiz", backref="chapter", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chapter {self.name}>"


# 4. Quiz Model
# Represents a quiz belonging to a specific chapter.
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    time_duration = db.Column(db.Integer, nullable=False, default=10)  # Duration in minutes
    is_published = db.Column(db.Boolean, nullable=False, default=False)  # Admin/Staff can toggle visibility

    # A quiz has multiple questions and scores
    questions = db.relationship("Question", backref="quiz", lazy=True, cascade="all, delete-orphan")
    scores = db.relationship("Score", backref="quiz", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quiz {self.title}>"


# 5. Question Model
# Represents a multiple-choice question in a quiz.
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    
    correct_option = db.Column(db.String(5), nullable=False)  # 'A', 'B', 'C', or 'D'
    marks = db.Column(db.Integer, nullable=False, default=1)  # Marks allocated for this question

    def __repr__(self):
        return f"<Question id={self.id} QuizID={self.quiz_id}>"


# 6. Score Model
# Represents the attempt score of a student (User) on a Quiz.
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    
    total_score = db.Column(db.Integer, nullable=False)  # Marks secured by the user
    time_taken = db.Column(db.Integer, nullable=False)  # Time taken in minutes or seconds
    date_taken = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Score UserID={self.user_id} QuizID={self.quiz_id} Score={self.total_score}>"
