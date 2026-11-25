from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import User, RegistrationCode
from wtforms import TextAreaField


class StudentRegisterForm(FlaskForm):
    matric_number = StringField(
        'Matric Number',
        validators=[Optional(), Length(min=5, max=30)]
    )

    full_name = StringField(
        'Full Name',
        validators=[DataRequired(), Length(min=3, max=100)]
    )

    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )

    level = SelectField(
        'Academic Level',
        choices=[
            ('', 'Select Your Level'),
            ('100L', '100 Level'),
            ('200L', '200 Level'),
            ('300L', '300 Level'),
            ('400L', '400 Level'),
            ('500L', '500 Level'),
            ('600L', '600 Level')
        ],
        validators=[DataRequired(message='Please select your academic level.')]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )

    submit = SubmitField('Register as Student')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

    def validate_matric_number(self, matric_number):
        if matric_number.data:
            matric = matric_number.data.strip().upper()
        user = User.query.filter_by(matric_number=matric_number.data).first()
        if user:
            raise ValidationError('Matric number already registered.')



class InterpreterRegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    code = StringField('Registration Code', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register as Interpreter')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')


class HOIRegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    code = StringField('Registration Code', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
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
    level = SelectField('Level', choices=[('100L', '100L'), ('200L', '200L'), ('300L', '300L'), ('400L', '400L'), ('500L', '500L'), ('600L', '600L')])
    department = StringField('Department')
    profile_picture = FileField('Profile Picture')
    submit = SubmitField('Update Profile')



class EditProfileForm(FlaskForm):
    full_name = StringField(
        'Full Name',
        validators=[DataRequired(), Length(min=3, max=100)]
    )

    matric_number = StringField(
        'Matric Number',
        validators=[Optional(), Length(min=5, max=30)]
    )

    department = SelectField(
        'Department',
        choices=[
            ('', 'Select Department'),
            ('Computer Science', 'Computer Science'),
            ('Special Education', 'Special Education'),
            ('Business Administration', 'Business Administration'),
            ('Political Science', 'Political Science'),
            ('Economic', 'Economic'),
            ('Mass Communication', 'Mass Communication'),
            ('Health Community', 'Health Community'),
            ('Nutrition and Dietetics', 'Nutrition and Dietetics'),
            ('Public Administration', 'Public Administration'),
            ('Law', 'Law'),
            ('International Relations and Diplomacy', 'International Relations and Diplomacy'),
            ('Public Health', 'Public Health')
        ],
        validators=[Optional()]
    )

    level = SelectField(
        'Level',
        choices=[
            ('', 'Select Level'),
            ('100L', '100L'),
            ('200L', '200L'),
            ('300L', '300L'),
            ('400L', '400L'),
            ('500L', '500L'),
            ('600L', '600L')
        ],
        validators=[DataRequired()]
    )

    profile_picture = FileField('Profile Picture')

    submit = SubmitField('Save Changes')



class TimetableForm(FlaskForm):
    course_code = StringField('Course Code', validators=[DataRequired(), Length(max=20)])
    course_title = StringField('Course Title', validators=[DataRequired(), Length(max=150)])
    # StringField works with your custom dropdowns (hidden inputs)
    day = StringField('Day', validators=[DataRequired(message='Please select a day.')])
    start_hour = StringField('Start Hour', validators=[DataRequired(message='Please select start hour.')])
    start_minute = StringField('Start Minute', validators=[DataRequired(message='Please select start minute.')])
    start_ampm = StringField('Start AM/PM', validators=[DataRequired(message='Please select AM or PM.')])
    end_hour = StringField('End Hour', validators=[DataRequired(message='Please select end hour.')])
    end_minute = StringField('End Minute', validators=[DataRequired(message='Please select end minute.')])
    end_ampm = StringField('End AM/PM', validators=[DataRequired(message='Please select AM or PM.')])
    venue = StringField('Venue', validators=[DataRequired()])
    lecturer = StringField('Lecturer Name', validators=[Optional()])
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