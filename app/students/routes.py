from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.student import Student, Enrollment
from app.models.academic import Program, Section
from app.utils.decorators import admin_required, super_admin_required
from app.utils.audit import log_action
from app.students.forms import StudentForm
from datetime import date

students_bp = Blueprint('students', __name__, url_prefix='/students')


@students_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    program_id = request.args.get('program_id', '', type=str)
    status = request.args.get('status', 'active')

    query = Student.query

    if status and status != 'all':
        query = query.filter_by(status=status)
    if q:
        query = query.filter(
            db.or_(
                Student.full_name.ilike(f'%{q}%'),
                Student.roll_number.ilike(f'%{q}%'),
            )
        )
    if program_id:
        query = query.filter_by(program_id=int(program_id))

    students = query.order_by(Student.roll_number).paginate(page=page, per_page=20, error_out=False)
    programs = Program.query.filter_by(active=True).order_by(Program.name).all()

    return render_template('students/index.html', students=students, programs=programs,
                           q=q, program_id=program_id, status=status)


@students_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    form = StudentForm()
    form.program_id.choices = [(p.id, p.name) for p in Program.query.filter_by(active=True).order_by(Program.name).all()]
    form.section_id.choices = [(0, '-- Select Section --')] + [
        (s.id, s.display_name) for s in Section.query.filter_by(active=True).order_by(Section.section_name).all()
    ]

    if form.validate_on_submit():
        existing = Student.query.filter_by(roll_number=form.roll_number.data.strip()).first()
        if existing:
            flash(f'Roll number "{form.roll_number.data}" is already registered.', 'danger')
        else:
            student = Student(
                roll_number=form.roll_number.data.strip().upper(),
                full_name=form.full_name.data.strip(),
                program_id=form.program_id.data,
                section_id=form.section_id.data if form.section_id.data else None,
                email=form.email.data.strip() if form.email.data else None,
                phone=form.phone.data.strip() if form.phone.data else None,
                gender=form.gender.data,
                admission_date=form.admission_date.data,
                status='active',
            )
            db.session.add(student)
            db.session.flush()

            if form.section_id.data:
                enroll = Enrollment(
                    student_id=student.id,
                    section_id=form.section_id.data,
                    start_date=form.admission_date.data,
                    status='active',
                )
                db.session.add(enroll)

            log_action(current_user.id, 'create', 'student', student.id,
                       f'Added student {student.roll_number}')
            db.session.commit()
            flash(f'Student {student.full_name} added successfully.', 'success')
            return redirect(url_for('students.detail', student_id=student.id))

    return render_template('students/form.html', form=form, title='Add Student')


@students_bp.route('/<int:student_id>')
@login_required
def detail(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('students/detail.html', student=student)


@students_bp.route('/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(student_id):
    student = Student.query.get_or_404(student_id)
    form = StudentForm(obj=student)
    form.program_id.choices = [(p.id, p.name) for p in Program.query.filter_by(active=True).order_by(Program.name).all()]
    form.section_id.choices = [(0, '-- Select Section --')] + [
        (s.id, s.display_name) for s in Section.query.filter_by(active=True).order_by(Section.section_name).all()
    ]

    if form.validate_on_submit():
        existing = Student.query.filter(
            Student.roll_number == form.roll_number.data.strip().upper(),
            Student.id != student_id
        ).first()
        if existing:
            flash(f'Roll number "{form.roll_number.data}" is taken by another student.', 'danger')
        else:
            student.roll_number = form.roll_number.data.strip().upper()
            student.full_name = form.full_name.data.strip()
            student.program_id = form.program_id.data
            student.section_id = form.section_id.data if form.section_id.data else None
            student.email = form.email.data.strip() if form.email.data else None
            student.phone = form.phone.data.strip() if form.phone.data else None
            student.gender = form.gender.data
            student.admission_date = form.admission_date.data
            log_action(current_user.id, 'update', 'student', student.id,
                       f'Updated student {student.roll_number}')
            db.session.commit()
            flash('Student record updated.', 'success')
            return redirect(url_for('students.detail', student_id=student.id))

    return render_template('students/form.html', form=form, title='Edit Student', student=student)


@students_bp.route('/<int:student_id>/archive', methods=['POST'])
@login_required
@admin_required
def archive(student_id):
    student = Student.query.get_or_404(student_id)
    student.status = 'archived'
    log_action(current_user.id, 'archive', 'student', student.id,
               f'Archived student {student.roll_number}')
    db.session.commit()
    flash(f'Student {student.full_name} has been archived.', 'warning')
    return redirect(url_for('students.index'))


@students_bp.route('/<int:student_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete(student_id):
    student = Student.query.get_or_404(student_id)
    if student.attendance_records.count() > 0:
        flash(f'Cannot delete student "{student.full_name}" because attendance records exist for them. You can Archive them instead.', 'danger')
        return redirect(url_for('students.index'))
    
    # Remove enrollments
    for e in student.enrollments.all():
        db.session.delete(e)

    roll = student.roll_number
    name = student.full_name
    log_action(current_user.id, 'delete', 'student', student.id,
               f'Deleted student {roll} ({name})')
    db.session.delete(student)
    db.session.commit()
    flash(f'Student "{name}" ({roll}) has been permanently deleted.', 'success')
    return redirect(url_for('students.index'))
