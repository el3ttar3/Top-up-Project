from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    @staticmethod
    def get(user_id):
        # This method is required by Flask-Login
        try:
            from app import supabase
            response = supabase.table('users').select("*").eq('id', user_id).execute()
            if response.data:
                user_data = response.data[0]
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email']
                )
        except Exception as e:
            print(f"Error loading user: {str(e)}")
        return None

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    duration = db.Column(db.String(50))
    skill_level = db.Column(db.String(50))
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    expertise = db.Column(db.String(100))
    bio = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    courses = db.relationship('Course', backref='instructor', lazy=True)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 