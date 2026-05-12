from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.String(20), nullable=False)
    year_group = db.Column(db.String(10), nullable=False)
    send_need = db.Column(db.String(50), nullable=False)
    ehcp = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updates = db.relationship('CommunicationUpdate', backref='student', lazy=True)

    def __repr__(self):
        return f'<Student {self.full_name}>'

class CommunicationUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author_role = db.Column(db.String(20), nullable=False)
    update_type = db.Column(db.String(50), nullable=False)
    mood = db.Column(db.String(10), nullable=True)
    message = db.Column(db.Text, nullable=False)
    alert_level = db.Column(db.String(20), default='Normal')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.relationship('User', backref='updates')

    def __repr__(self):
        return f'<Update {self.id} for Student {self.student_id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))