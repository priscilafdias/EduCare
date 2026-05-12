from flask_mail import Message
from app import mail
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User, Student, CommunicationUpdate
from datetime import datetime
from functools import wraps

auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)

MOODS = [
    ('😄', 'Happy'),
    ('😴', 'Tired'),
    ('😠', 'Angry'),
    ('😪', 'Sleepy'),
    ('🤫', 'Quiet'),
    ('😰', 'Anxious'),
    ('😒', 'Not in the mood')
]

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ['teacher', 'ta']:
            flash('Access restricted to staff only.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@main.route('/')
@login_required
def dashboard():
    updates = CommunicationUpdate.query.order_by(CommunicationUpdate.created_at.desc()).limit(5).all()
    if current_user.role in ['teacher', 'ta']:
        students = Student.query.all()
    elif current_user.role in ['parent', 'student']:
        students = [current_user.linked_student] if current_user.linked_student else []
    else:
        students = []
    return render_template('dashboard.html', students=students, updates=updates)

@main.route('/students')
@login_required
@staff_required
def students():
    students = Student.query.all()
    return render_template('students.html', students=students)

@main.route('/students/add', methods=['GET', 'POST'])
@login_required
@staff_required
def add_student():
    if request.method == 'POST':
        student = Student(
            full_name=request.form.get('full_name'),
            date_of_birth=request.form.get('date_of_birth'),
            year_group=request.form.get('year_group'),
            send_need=request.form.get('send_need'),
            ehcp=True if request.form.get('ehcp') else False,
            notes=request.form.get('notes')
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('main.students'))
    return render_template('add_student.html')

@main.route('/students/<int:id>')
@login_required
def student_profile(id):
    student = Student.query.get_or_404(id)
    if current_user.role in ['parent', 'student']:
        if not current_user.linked_student or current_user.linked_student.id != id:
            flash('Access restricted.', 'danger')
            return redirect(url_for('main.dashboard'))
    updates = CommunicationUpdate.query.filter_by(student_id=id).order_by(CommunicationUpdate.created_at.desc()).all()
    return render_template('student_profile.html', student=student, updates=updates)

@main.route('/students/<int:id>/update', methods=['GET', 'POST'])
@login_required
def add_update(id):
    student = Student.query.get_or_404(id)
    if current_user.role in ['parent', 'student']:
        if not current_user.linked_student or current_user.linked_student.id != id:
            flash('Access restricted.', 'danger')
            return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        update = CommunicationUpdate(
            student_id=id,
            author_id=current_user.id,
            author_role=current_user.role,
            update_type=request.form.get('update_type'),
            mood=request.form.get('mood'),
            message=request.form.get('message'),
            alert_level=request.form.get('alert_level')
        )
        db.session.add(update)
        db.session.commit()
        flash('Update posted!', 'success')
        return redirect(url_for('main.student_profile', id=id))
    return render_template('add_update.html', student=student, moods=MOODS)

@main.route('/board')
@login_required
def board():
    if current_user.role in ['teacher', 'ta']:
        updates = CommunicationUpdate.query.order_by(CommunicationUpdate.created_at.desc()).all()
    elif current_user.role in ['parent', 'student']:
        if current_user.linked_student:
            updates = CommunicationUpdate.query.filter_by(
                student_id=current_user.linked_student.id
            ).order_by(CommunicationUpdate.created_at.desc()).all()
        else:
            updates = []
    else:
        updates = []
    return render_template('board.html', updates=updates)

@main.route('/admin/link', methods=['GET', 'POST'])
@login_required
@staff_required
def link_user():
    users = User.query.filter(User.role.in_(['parent', 'student'])).all()
    students = Student.query.all()
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        student_id = request.form.get('student_id')
        user = User.query.get(user_id)
        user.student_id = student_id
        db.session.commit()
        flash(f'{user.username} linked successfully!', 'success')
        return redirect(url_for('main.link_user'))
    return render_template('link_user.html', users=users, students=students)

@main.route('/students/<int:id>/report', methods=['GET', 'POST'])
@login_required
@staff_required
def student_report(id):
    student = Student.query.get_or_404(id)
    updates = CommunicationUpdate.query.filter_by(
        student_id=id
    ).order_by(CommunicationUpdate.created_at.desc()).all()
    
    mood_counts = {}
    for update in updates:
        if update.mood:
            mood = update.mood
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
    
    alert_counts = {
        'Normal': sum(1 for u in updates if u.alert_level == 'Normal'),
        'Needs Attention': sum(1 for u in updates if u.alert_level == 'Needs Attention'),
        'Urgent': sum(1 for u in updates if u.alert_level == 'Urgent'),
    }

    if request.method == 'POST':
        recipient = request.form.get('email')
        report_text = f"""
EduCare Progress Report
=======================
Student: {student.full_name}
Year Group: {student.year_group}
SEND Need: {student.send_need}
EHCP: {'Yes' if student.ehcp else 'No'}

Total Updates: {len(updates)}
Urgent Alerts: {alert_counts['Urgent']}
Needs Attention: {alert_counts['Needs Attention']}

Recent Updates:
"""
        for update in updates[:5]:
            report_text += f"""
- [{update.author_role.upper()}] {update.update_type}
  {update.message}
  {update.created_at.strftime('%d %b %Y, %H:%M')}
"""
        try:
            msg = Message(
                subject=f'EduCare Report - {student.full_name}',
                recipients=[recipient],
                body=report_text
            )
            mail.send(msg)
            flash('Report sent successfully!', 'success')
        except Exception as e:
            flash('Error sending email. Please check the address.', 'danger')
        return redirect(url_for('main.student_report', id=id))

    return render_template('report.html', student=student, updates=updates, mood_counts=mood_counts, alert_counts=alert_counts)