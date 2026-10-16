from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, hoi, interpreter, student

    # Student specific
    matric_number = db.Column(db.String(30), unique=True, nullable=True)
    department = db.Column(db.String(100), nullable=True)
    department_colour = db.Column(db.String(20), nullable=True)
    level = db.Column(db.String(10), nullable=True)
    profile_picture = db.Column(db.String(200), nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    is_class_rep = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Fixed relationship
    codes_created = db.relationship(
        'RegistrationCode',
        foreign_keys='RegistrationCode.created_by',
        backref='created_by_user',
        lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.full_name} ({self.role})>'


class RegistrationCode(db.Model):
    __tablename__ = 'registration_codes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(12), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # interpreter or hoi
    is_used = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)
    used_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return f'<Code {self.code} - {self.role}>'


def generate_registration_code():
    return secrets.token_hex(4).upper()


class Timetable(db.Model):
    __tablename__ = 'timetables'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_code = db.Column(db.String(20), nullable=False)
    course_title = db.Column(db.String(150), nullable=False)
    day = db.Column(db.String(20), nullable=False)  # Monday, Tuesday, etc.
    time = db.Column(db.String(30), nullable=False)  # e.g. 09:00 - 11:00
    venue = db.Column(db.String(100), nullable=False)
    lecturer = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    student = db.relationship('User', backref='timetables')
    department = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(10), nullable=False)  # 100L, 200L, etc.

    def __repr__(self):
        return f'<Timetable {self.course_code} on {self.day}>'


class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    timetable_id = db.Column(db.Integer, db.ForeignKey('timetables.id'), nullable=False)
    interpreter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    status = db.Column(db.String(20), default='Pending')
    # Possible values: Pending, Assigned, Present, Absent

    assigned_at = db.Column(db.DateTime, nullable=True)
    marked_by_student = db.Column(db.String(20), nullable=True)  # Present / Absent
    marked_by_interpreter = db.Column(db.String(20), nullable=True)
    marked_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    timetable = db.relationship('Timetable', backref=db.backref('assignment', uselist=False))
    interpreter = db.relationship('User', backref='assignments')

    def __repr__(self):
        return f'<Assignment {self.id} - {self.status}>'


class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    interpreter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    timetable_id = db.Column(db.Integer, db.ForeignKey('timetables.id'), nullable=True)

    category = db.Column(db.String(50), nullable=False)  # Absent, Late, Wrong Interpreter, Other
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Open')  # Open, In Progress, Resolved
    reply = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    replied_at = db.Column(db.DateTime, nullable=True)

    student = db.relationship('User', foreign_keys=[student_id], backref='complaints_made')
    interpreter = db.relationship('User', foreign_keys=[interpreter_id], backref='complaints_received')
    timetable = db.relationship('Timetable', backref='complaints')

    def __repr__(self):
        return f'<Complaint {self.id} - {self.category}>'