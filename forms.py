from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User, RegistrationCode
from wtforms import TextAreaField

class StudentRegisterForm(FlaskForm):
    matric_number = StringField('Matric Number', validators=[DataRequired(), Length(min=5, max=30)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register as Student')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

    def validate_matric_number(self, matric_number):
        user = User.query.filter_by(matric_number=matric_number.data).first()
        if user:
            raise ValidationError('Matric number already registered.')


class InterpreterRegisterForm(FlaskForm):
    code = StringField('Registration Code', validators=[DataRequired()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register as Interpreter')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')


class HOIRegisterForm(FlaskForm):
    code = StringField('Registration Code', validators=[DataRequired()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register as HOI')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    level = SelectField('Level', choices=[('100L', '100L'), ('200L', '200L'), ('300L', '300L'), ('400L', '400L')])
    department = StringField('Department')
    profile_picture = FileField('Profile Picture')
    submit = SubmitField('Update Profile')


class EditProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    level = SelectField('Level', choices=[
        ('', 'Select Level'),
        ('100L', '100L'),
        ('200L', '200L'),
        ('300L', '300L'),
        ('400L', '400L'),
        ('500L', '500L')
    ], validators=[DataRequired()])
    profile_picture = FileField('Profile Picture')
    submit = SubmitField('Save Changes')


class TimetableForm(FlaskForm):
    course_code = StringField('Course Code', validators=[DataRequired(), Length(max=20)])
    course_title = StringField('Course Title', validators=[DataRequired(), Length(max=150)])
    day = SelectField('Day', choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday')
    ], validators=[DataRequired()])

    # New time fields
    start_hour = SelectField('Start Hour', choices=[(str(i), f'{i:02d}') for i in range(1, 13)], validators=[DataRequired()])
    start_minute = SelectField('Start Minute', choices=[('00', '00'), ('30', '30')], validators=[DataRequired()])
    start_ampm = SelectField('AM/PM', choices=[('AM', 'AM'), ('PM', 'PM')], validators=[DataRequired()])

    end_hour = SelectField('End Hour', choices=[(str(i), f'{i:02d}') for i in range(1, 13)], validators=[DataRequired()])
    end_minute = SelectField('End Minute', choices=[('00', '00'), ('30', '30')], validators=[DataRequired()])
    end_ampm = SelectField('AM/PM', choices=[('AM', 'AM'), ('PM', 'PM')], validators=[DataRequired()])

    venue = StringField('Venue', validators=[DataRequired()])
    lecturer = StringField('Lecturer Name')
    submit = SubmitField('Add Class')

class ComplaintForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('Interpreter Absent', 'Interpreter Absent'),
        ('Interpreter Late', 'Interpreter Late'),
        ('Wrong Interpreter', 'Wrong Interpreter'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    message = TextAreaField('Describe the problem', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Submit Complaint')