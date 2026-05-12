from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User, Student

auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)

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
    students = Student.query.all()
    return render_template('dashboard.html', students=students)

@main.route('/students')
@login_required
def students():
    students = Student.query.all()
    return render_template('students.html', students=students)

@main.route('/students/add', methods=['GET', 'POST'])
@login_required
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
    return render_template('student_profile.html', student=student)