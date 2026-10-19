from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.faculty import Faculty, FacultyAssignment
from app.models.academic import Department, Section, Subject, AcademicYear
from app.utils.decorators import admin_required, super_admin_required
from app.utils.audit import log_action
from app.faculty.forms import FacultyForm, AssignmentForm

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')


@faculty_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    dept_id = request.args.get('dept_id', '', type=str)
    status = request.args.get('status', 'active')

    query = Faculty.query

    if status and status != 'all':
        query = query.filter_by(status=status)
    if q:
        query = query.filter(
            db.or_(
                Faculty.full_name.ilike(f'%{q}%'),
                Faculty.employee_id.ilike(f'%{q}%'),
            )
        )
    if dept_id:
        query = query.filter_by(department_id=int(dept_id))

    faculty_list = query.order_by(Faculty.full_name).paginate(page=page, per_page=20, error_out=False)
    departments = Department.query.filter_by(active=True).order_by(Department.name).all()

    return render_template('faculty/index.html', faculty_list=faculty_list,
                           departments=departments, q=q, dept_id=dept_id, status=status)


@faculty_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    form = FacultyForm()
    form.department_id.choices = [
        (d.id, d.name) for d in Department.query.filter_by(active=True).order_by(Department.name).all()
    ]

    if form.validate_on_submit():
        existing = Faculty.query.filter_by(employee_id=form.employee_id.data.strip()).first()
        if existing:
            flash(f'Employee ID "{form.employee_id.data}" is already registered.', 'danger')
        else:
            faculty = Faculty(
                employee_id=form.employee_id.data.strip().upper(),
                full_name=form.full_name.data.strip(),
                department_id=form.department_id.data,
                designation=form.designation.data.strip() if form.designation.data else None,
                email=form.email.data.strip() if form.email.data else None,
                phone=form.phone.data.strip() if form.phone.data else None,
                qualification=form.qualification.data.strip() if form.qualification.data else None,
                joining_date=form.joining_date.data,
                status='active',
            )
            db.session.add(faculty)
            db.session.flush()
            log_action(current_user.id, 'create', 'faculty', faculty.id,
                       f'Added faculty {faculty.employee_id}')
            db.session.commit()
            flash(f'Faculty member {faculty.full_name} added successfully.', 'success')
            return redirect(url_for('faculty.detail', faculty_id=faculty.id))

    return render_template('faculty/form.html', form=form, title='Add Faculty')


@faculty_bp.route('/<int:faculty_id>')
@login_required
def detail(faculty_id):
    member = Faculty.query.get_or_404(faculty_id)
    assignments = FacultyAssignment.query.filter_by(faculty_id=faculty_id).all()
    return render_template('faculty/detail.html', member=member, assignments=assignments)


@faculty_bp.route('/<int:faculty_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(faculty_id):
    member = Faculty.query.get_or_404(faculty_id)
    form = FacultyForm(obj=member)
    form.department_id.choices = [
        (d.id, d.name) for d in Department.query.filter_by(active=True).order_by(Department.name).all()
    ]

    if form.validate_on_submit():
        existing = Faculty.query.filter(
            Faculty.employee_id == form.employee_id.data.strip().upper(),
            Faculty.id != faculty_id
        ).first()
        if existing:
            flash(f'Employee ID "{form.employee_id.data}" is taken by another faculty member.', 'danger')
        else:
            member.employee_id = form.employee_id.data.strip().upper()
            member.full_name = form.full_name.data.strip()
            member.department_id = form.department_id.data
            member.designation = form.designation.data.strip() if form.designation.data else None
            member.email = form.email.data.strip() if form.email.data else None
            member.phone = form.phone.data.strip() if form.phone.data else None
            member.qualification = form.qualification.data.strip() if form.qualification.data else None
            member.joining_date = form.joining_date.data
            log_action(current_user.id, 'update', 'faculty', member.id,
                       f'Updated faculty {member.employee_id}')
            db.session.commit()
            flash('Faculty record updated.', 'success')
            return redirect(url_for('faculty.detail', faculty_id=member.id))

    return render_template('faculty/form.html', form=form, title='Edit Faculty', member=member)


@faculty_bp.route('/<int:faculty_id>/archive', methods=['POST'])
@login_required
@admin_required
def archive(faculty_id):
    member = Faculty.query.get_or_404(faculty_id)
    member.status = 'archived'
    log_action(current_user.id, 'archive', 'faculty', member.id,
               f'Archived faculty {member.employee_id}')
    db.session.commit()
    flash(f'{member.full_name} has been archived.', 'warning')
    return redirect(url_for('faculty.index'))


# ---- Teaching Assignments ----

@faculty_bp.route('/assignments')
@login_required
@admin_required
def assignments():
    all_assignments = FacultyAssignment.query.order_by(FacultyAssignment.id.desc()).all()
    return render_template('faculty/assignments.html', assignments=all_assignments)


@faculty_bp.route('/assignments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_assignment():
    form = AssignmentForm()
    form.faculty_id.choices = [
        (f.id, f'{f.full_name} ({f.employee_id})')
        for f in Faculty.query.filter_by(status='active').order_by(Faculty.full_name).all()
    ]
    form.section_id.choices = [
        (s.id, s.display_name)
        for s in Section.query.filter_by(active=True).order_by(Section.section_name).all()
    ]
    form.subject_id.choices = [
        (sub.id, f'{sub.code} - {sub.title}')
        for sub in Subject.query.filter_by(active=True).order_by(Subject.code).all()
    ]
    form.academic_year_id.choices = [
        (y.id, y.label)
        for y in AcademicYear.query.order_by(AcademicYear.start_date.desc()).all()
    ]

    if form.validate_on_submit():
        existing = FacultyAssignment.query.filter_by(
            faculty_id=form.faculty_id.data,
            section_id=form.section_id.data,
            subject_id=form.subject_id.data,
            academic_year_id=form.academic_year_id.data,
        ).first()
        if existing:
            flash('This assignment already exists.', 'warning')
        else:
            assignment = FacultyAssignment(
                faculty_id=form.faculty_id.data,
                section_id=form.section_id.data,
                subject_id=form.subject_id.data,
                academic_year_id=form.academic_year_id.data,
            )
            db.session.add(assignment)
            db.session.flush()
            log_action(current_user.id, 'create', 'faculty_assignment', assignment.id,
                       f'Assigned faculty {form.faculty_id.data} to section {form.section_id.data}')
            db.session.commit()
            flash('Teaching assignment created.', 'success')
            return redirect(url_for('faculty.assignments'))

    return render_template('faculty/assignment_form.html', form=form, title='Add Teaching Assignment')


@faculty_bp.route('/<int:faculty_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete(faculty_id):
    member = Faculty.query.get_or_404(faculty_id)
    if member.attendance_sessions.count() > 0:
        flash(f'Cannot delete faculty member "{member.full_name}" because attendance registers are logged under their name. You can Archive them instead.', 'danger')
        return redirect(url_for('faculty.index'))
    
    # Remove any linked user account profile link
    if member.user_account:
        member.user_account.faculty_id = None

    # Remove any faculty assignments
    for a in member.assignments.all():
        db.session.delete(a)

    emp_id = member.employee_id
    full_name = member.full_name
    log_action(current_user.id, 'delete', 'faculty', member.id,
               f'Deleted faculty {emp_id} ({full_name})')
    db.session.delete(member)
    db.session.commit()
    flash(f'Faculty member "{full_name}" ({emp_id}) has been permanently deleted.', 'success')
    return redirect(url_for('faculty.index'))


@faculty_bp.route('/assignments/<int:assignment_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_assignment(assignment_id):
    assignment = FacultyAssignment.query.get_or_404(assignment_id)
    faculty_name = assignment.faculty.full_name if assignment.faculty else 'Unknown'
    subj_code = assignment.subject.code if assignment.subject else 'Unknown'
    log_action(current_user.id, 'delete', 'faculty_assignment', assignment.id,
               f'Deleted assignment {faculty_name} -> {subj_code}')
    db.session.delete(assignment)
    db.session.commit()
    flash(f'Teaching assignment for {faculty_name} ({subj_code}) deleted.', 'success')
    return redirect(url_for('faculty.assignments'))
