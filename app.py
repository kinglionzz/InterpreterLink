from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, RegistrationCode, generate_registration_code
from forms import StudentRegisterForm, InterpreterRegisterForm, HOIRegisterForm, LoginForm, ProfileForm, EditProfileForm
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from models import Assignment
from datetime import datetime

def auto_assign_interpreter(timetable):
    """
    Improved auto-assignment with strict time conflict checking.
    """
    from models import Assignment, Timetable, User
    from datetime import datetime

    MAX_CLASSES_PER_DAY = 3

    interpreters = User.query.filter_by(role='interpreter', is_active=True).all()
    if not interpreters:
        return None

    available = []

    for interp in interpreters:
        # 1. Check time conflict (same day + same time)
        conflict = (
            Assignment.query
            .join(Timetable)
            .filter(
                Assignment.interpreter_id == interp.id,
                Timetable.day == timetable.day,
                Timetable.time == timetable.time
            )
            .first()
        )

        if conflict:
            continue  # This interpreter is already busy at this exact time

        # 2. Count how many classes this interpreter has on this day
        day_count = (
            Assignment.query
            .join(Timetable)
            .filter(
                Assignment.interpreter_id == interp.id,
                Timetable.day == timetable.day
            )
            .count()
        )

        if day_count >= MAX_CLASSES_PER_DAY:
            continue

        available.append({
            'interpreter': interp,
            'day_count': day_count
        })

    if not available:
        return None

    # Prefer the least busy interpreter
    available.sort(key=lambda x: x['day_count'])
    best = available[0]['interpreter']

    assignment = Assignment(
        timetable_id=timetable.id,
        interpreter_id=best.id,
        status='Assigned',
        assigned_at=datetime.utcnow()
    )
    db.session.add(assignment)
    db.session.commit()

    return best

from forms import ComplaintForm
from models import Complaint

@app.route('/student/complaints', methods=['GET', 'POST'])
@login_required
def student_complaints():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    form = ComplaintForm()

    if form.validate_on_submit():
        complaint = Complaint(
            student_id=current_user.id,
            category=form.category.data,
            message=form.message.data,
            status='Open'
        )
        db.session.add(complaint)
        db.session.commit()

        flash('Your complaint has been submitted successfully.', 'success')
        return redirect(url_for('student_complaints'))

    complaints = Complaint.query.filter_by(student_id=current_user.id).order_by(Complaint.created_at.desc()).all()

    return render_template('student_complaints.html', form=form, complaints=complaints)


# ========== HELPER: Detect Department & Colour from Matric ==========
def detect_department(matric):
    matric = matric.upper()
    if matric.startswith('CSC') or 'CSC' in matric:
        return 'Computer Science', '#FFD700'      # Yellow
    elif matric.startswith('EDU') or 'EDU' in matric:
        return 'Special Education', '#722F37'     # Wine
    elif matric.startswith('BUS') or 'BUS' in matric:
        return 'Business Administration', '#000080'
    elif matric.startswith('POL') or 'POL' in matric:
        return 'Political Science', '#000080'
    elif matric.startswith('ENG') or 'ENG' in matric:
        return 'Engineering', '#32CD32'
    else:
        return 'General', '#808080'               # Grey


# ========== ROUTES ==========

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'hoi':
            return redirect(url_for('hoi_dashboard'))
        elif current_user.role == 'interpreter':
            return redirect(url_for('interpreter_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))


@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = StudentRegisterForm()
    if form.validate_on_submit():
        department, colour = detect_department(form.matric_number.data)

        user = User(
            email=form.email.data.lower(),
            full_name=form.full_name.data,
            role='student',
            matric_number=form.matric_number.data.upper(),
            department=department,
            department_colour=colour
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register_student.html', form=form)


@app.route('/register/interpreter', methods=['GET', 'POST'])
def register_interpreter():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = InterpreterRegisterForm()
    if form.validate_on_submit():
        code = RegistrationCode.query.filter_by(code=form.code.data.upper(), role='interpreter', is_used=False).first()
        if not code:
            flash('Invalid or already used registration code.', 'danger')
            return render_template('register_interpreter.html', form=form)

        user = User(
            email=form.email.data.lower(),
            full_name=form.full_name.data,
            role='interpreter'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # get user.id

        code.is_used = True
        code.used_at = datetime.utcnow()
        code.used_by = user.id
        db.session.commit()

        flash('Interpreter registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register_interpreter.html', form=form)


@app.route('/register/hoi', methods=['GET', 'POST'])
def register_hoi():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = HOIRegisterForm()
    if form.validate_on_submit():
        code = RegistrationCode.query.filter_by(code=form.code.data.upper(), role='hoi', is_used=False).first()
        if not code:
            flash('Invalid or already used registration code.', 'danger')
            return render_template('register_hoi.html', form=form)

        user = User(
            email=form.email.data.lower(),
            full_name=form.full_name.data,
            role='hoi'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        code.is_used = True
        code.used_at = datetime.utcnow()
        code.used_by = user.id
        db.session.commit()

        flash('HOI registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register_hoi.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Wrong email or password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    users = User.query.order_by(User.role, User.full_name).all()
    return render_template('admin_users.html', users=users)


@app.route('/admin/users/delete/<int:user_id>')
@login_required
def admin_delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)

    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own admin account.', 'danger')
        return redirect(url_for('admin_users'))

    # If interpreter → delete their assignments first
    if user.role == 'interpreter':
        Assignment.query.filter_by(interpreter_id=user.id).delete()

    # If student → delete their timetables + assignments
    if user.role == 'student':
        timetables = Timetable.query.filter_by(student_id=user.id).all()
        for t in timetables:
            if t.assignment:
                db.session.delete(t.assignment)
            db.session.delete(t)

    db.session.delete(user)
    db.session.commit()

    flash(f'User "{user.full_name}" has been deleted.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/student/mark/<int:assignment_id>/<status>')
@login_required
def student_mark_attendance(assignment_id, status):
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    if status not in ['Present', 'Absent']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('student_timetable'))

    assignment = Assignment.query.get_or_404(assignment_id)

    # Security check: only the student who owns the class can mark it
    if assignment.timetable.student_id != current_user.id:
        flash('You cannot mark this assignment.', 'danger')
        return redirect(url_for('student_timetable'))

    assignment.marked_by_student = status
    assignment.status = status
    assignment.marked_at = datetime.utcnow()
    db.session.commit()

    flash(f'Interpreter marked as {status}.', 'success')
    return redirect(url_for('student_timetable'))

@app.route('/admin/toggle-class-rep/<int:user_id>')
@login_required
def toggle_class_rep(user_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)

    if user.role != 'student':
        flash('Only students can be Class Reps.', 'danger')
        return redirect(url_for('admin_users'))

    user.is_class_rep = not user.is_class_rep
    db.session.commit()

    status = "now a Class Rep" if user.is_class_rep else "no longer a Class Rep"
    flash(f'{user.full_name} is {status}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/student/mark-attendance/<int:assignment_id>/<status>')
@login_required
def mark_attendance(assignment_id, status):
    if current_user.role != 'student' or not current_user.is_class_rep:
        flash('Only the Class Representative can mark attendance.', 'danger')
        return redirect(url_for('student_timetable'))

    if status not in ['Present', 'Absent']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('student_timetable'))

    assignment = Assignment.query.get_or_404(assignment_id)

    # Security check: make sure this class belongs to the Class Rep's department & level
    if (assignment.timetable.department != current_user.department or
        assignment.timetable.level != current_user.level):
        flash('You cannot mark this class.', 'danger')
        return redirect(url_for('student_timetable'))

    assignment.status = status
    assignment.marked_by_student = status
    assignment.marked_at = datetime.utcnow()
    db.session.commit()

    flash(f'Interpreter marked as {status}.', 'success')
    return redirect(url_for('student_timetable'))

@app.route('/hoi/dashboard')
@login_required
def hoi_dashboard():
    if current_user.role != 'hoi':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    classes = (
        Timetable.query
        .order_by(Timetable.day, Timetable.time, Timetable.department)
        .all()
    )

    interpreters = User.query.filter_by(role='interpreter', is_active=True).all()
    total_interpreters = len(interpreters)

    # Count open complaints
    open_complaints_count = Complaint.query.filter_by(status='Open').count()

    from collections import defaultdict
    slot_summary = defaultdict(lambda: {'total': 0, 'assigned': 0, 'pending': 0})

    for c in classes:
        key = f"{c.day} | {c.time}"
        slot_summary[key]['total'] += 1
        if c.assignment and c.assignment.interpreter_id:
            slot_summary[key]['assigned'] += 1
        else:
            slot_summary[key]['pending'] += 1

    return render_template(
        'hoi_dashboard.html',
        classes=classes,
        interpreters=interpreters,
        total_interpreters=total_interpreters,
        slot_summary=dict(slot_summary),
        open_complaints_count=open_complaints_count
    )

@app.route('/hoi/complaints')
@login_required
def hoi_complaints():
    if current_user.role != 'hoi':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    return render_template('hoi_complaints.html', complaints=complaints)


@app.route('/hoi/complaints/reply/<int:complaint_id>', methods=['GET', 'POST'])
@login_required
def hoi_reply_complaint(complaint_id):
    if current_user.role != 'hoi':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    complaint = Complaint.query.get_or_404(complaint_id)

    if request.method == 'POST':
        reply = request.form.get('reply')
        if not reply:
            flash('Reply cannot be empty.', 'danger')
            return redirect(url_for('hoi_reply_complaint', complaint_id=complaint_id))

        complaint.reply = reply
        complaint.status = 'Resolved'
        complaint.replied_at = datetime.utcnow()
        db.session.commit()

        flash('Reply sent successfully.', 'success')
        return redirect(url_for('hoi_complaints'))

    return render_template('hoi_reply_complaint.html', complaint=complaint)


# ========== DASHBOARDS (Temporary simple versions) ==========

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    # Get shared timetable for this student's department + level
    classes = Timetable.query.filter_by(
        department=current_user.department,
        level=current_user.level
    ).all()

    total_classes = len(classes)
    assigned_classes = 0
    present_count = 0

    for c in classes:
        if c.assignment and c.assignment.interpreter_id:
            assigned_classes += 1
            if c.assignment.status == 'Present':
                present_count += 1

    # Count student's complaints
    complaints_count = Complaint.query.filter_by(student_id=current_user.id).count()

    return render_template(
        'student_dashboard.html',
        total_classes=total_classes,
        assigned_classes=assigned_classes,
        present_count=present_count,
        complaints_count=complaints_count
    )

@app.route('/interpreter/dashboard')
@login_required
def interpreter_dashboard():
    if current_user.role != 'interpreter':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    assignments = Assignment.query.filter_by(interpreter_id=current_user.id).all()
    return render_template('interpreter_dashboard.html', assignments=assignments)


@app.route('/interpreter/assignments')
@login_required
def interpreter_assignments():
    if current_user.role != 'interpreter':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    assignments = (
        Assignment.query
        .filter_by(interpreter_id=current_user.id)
        .join(Timetable)
        .order_by(Timetable.day, Timetable.time)
        .all()
    )

    return render_template('interpreter_assignments.html', assignments=assignments)


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    codes = RegistrationCode.query.order_by(RegistrationCode.created_at.desc()).all()
    return render_template('admin_dashboard.html', codes=codes)


@app.route('/admin/generate-code/<role>')
@login_required
def generate_code(role):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    if role not in ['interpreter', 'hoi']:
        flash('Invalid role.', 'danger')
        return redirect(url_for('admin_dashboard'))

    new_code = RegistrationCode(
        code=generate_registration_code(),
        role=role,
        created_by=current_user.id
    )
    db.session.add(new_code)
    db.session.commit()

    flash(f'New {role.upper()} code generated: {new_code.code}', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('register.html')

from werkzeug.utils import secure_filename
import os

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.level = form.level.data

        if form.profile_picture.data:
            picture = form.profile_picture.data
            filename = secure_filename(picture.filename)
            unique_name = f"user_{current_user.id}_{filename}"

            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            picture.save(os.path.join(upload_folder, unique_name))
            current_user.profile_picture = unique_name

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    form.full_name.data = current_user.full_name
    form.level.data = current_user.level

    return render_template('edit_profile.html', form=form)


from forms import TimetableForm
from models import Timetable, Assignment

@app.route('/student/timetable', methods=['GET', 'POST'])
@login_required
def student_timetable():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    form = TimetableForm()

    if form.validate_on_submit():
        if not current_user.is_class_rep:
            flash('Only the Class Representative can upload the timetable.', 'danger')
            return redirect(url_for('student_timetable'))

        # Build the time properly
        start_time = f"{form.start_hour.data}:{form.start_minute.data} {form.start_ampm.data}"
        end_time = f"{form.end_hour.data}:{form.end_minute.data} {form.end_ampm.data}"
        full_time = f"{start_time} - {end_time}"

        new_class = Timetable(
            student_id=current_user.id,
            department=current_user.department,
            level=current_user.level,
            course_code=form.course_code.data.upper(),
            course_title=form.course_title.data,
            day=form.day.data,
            time=full_time,
            venue=form.venue.data,
            lecturer=form.lecturer.data
        )
        db.session.add(new_class)
        db.session.commit()

        # Auto assign interpreter
        assigned_interpreter = auto_assign_interpreter(new_class)

        if assigned_interpreter:
            flash(f'Class added and Interpreter {assigned_interpreter.full_name} assigned!', 'success')
        else:
            flash('Class added. No interpreter available yet.', 'warning')

        return redirect(url_for('student_timetable'))

    # All students in the same Department + Level can see the shared timetable
    classes = Timetable.query.filter_by(
        department=current_user.department,
        level=current_user.level
    ).order_by(Timetable.day, Timetable.time).all()

    return render_template(
        'student_timetable.html',
        form=form,
        classes=classes,
        is_class_rep=current_user.is_class_rep
    )


@app.route('/student/timetable/delete/<int:id>')
@login_required
def delete_timetable(id):
    if current_user.role != 'student' or not current_user.is_class_rep:
        flash('Only the Class Representative can delete classes.', 'danger')
        return redirect(url_for('student_timetable'))

    class_item = Timetable.query.get_or_404(id)

    # Make sure it belongs to the same department & level
    if class_item.department != current_user.department or class_item.level != current_user.level:
        flash('You cannot delete this class.', 'danger')
        return redirect(url_for('student_timetable'))

    if class_item.assignment:
        db.session.delete(class_item.assignment)

    db.session.delete(class_item)
    db.session.commit()
    flash('Class deleted successfully.', 'info')
    return redirect(url_for('student_timetable'))

@app.route('/hoi/reassign/<int:timetable_id>', methods=['GET', 'POST'])
@login_required
def hoi_reassign(timetable_id):
    if current_user.role != 'hoi':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    timetable = Timetable.query.get_or_404(timetable_id)
    interpreters = User.query.filter_by(role='interpreter', is_active=True).all()

    if request.method == 'POST':
        interpreter_id = request.form.get('interpreter_id')

        if not interpreter_id:
            flash('Please select an interpreter.', 'danger')
            return redirect(url_for('hoi_reassign', timetable_id=timetable_id))

        # Delete old assignment if exists
        if timetable.assignment:
            db.session.delete(timetable.assignment)

        # Create new assignment
        new_assignment = Assignment(
            timetable_id=timetable.id,
            interpreter_id=int(interpreter_id),
            status='Assigned',
            assigned_at=datetime.utcnow()
        )
        db.session.add(new_assignment)
        db.session.commit()

        flash('Interpreter re-assigned successfully!', 'success')
        return redirect(url_for('hoi_dashboard'))

    return render_template(
        'hoi_reassign.html',
        timetable=timetable,
        interpreters=interpreters
    )

# ========== CREATE TABLES + FIRST ADMIN ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Create first Admin if none exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                email='admin@interpreterlink.com',
                full_name='System Admin',
                role='admin'
            )
            admin.set_password('admin123')  # Change this password later!
            db.session.add(admin)
            db.session.commit()
            print("Admin created → Email: admin@interpreterlink.com | Password: admin123")

    app.run(debug=True)
