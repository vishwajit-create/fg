from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.academic import Department, Program, AcademicYear, Section, Subject
from app.utils.decorators import admin_required, super_admin_required
from app.utils.audit import log_action
from app.academic.forms import (DepartmentForm, ProgramForm, AcademicYearForm,
                                  SectionForm, SubjectForm)

academic_bp = Blueprint('academic', __name__, url_prefix='/academic')


# ---- Departments ----

@academic_bp.route('/departments')
@login_required
@admin_required
def departments():
    depts = Department.query.order_by(Department.name).all()
    return render_template('academic/departments.html', depts=depts)


@academic_bp.route('/departments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        existing = Department.query.filter(
            db.func.lower(Department.code) == form.code.data.strip().lower()
        ).first()
        if existing:
            flash(f'Department code "{form.code.data}" already exists.', 'danger')
        else:
            dept = Department(
                code=form.code.data.strip().upper(),
                name=form.name.data.strip(),
                description=form.description.data.strip() if form.description.data else None,
            )
            db.session.add(dept)
            db.session.flush()
            log_action(current_user.id, 'create', 'department', dept.id, f'Created dept {dept.code}')
            db.session.commit()
            flash(f'Department "{dept.name}" created.', 'success')
            return redirect(url_for('academic.departments'))
    return render_template('academic/dept_form.html', form=form, title='Add Department')


@academic_bp.route('/departments/<int:dept_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    form = DepartmentForm(obj=dept)
    if form.validate_on_submit():
        existing = Department.query.filter(
            db.func.lower(Department.code) == form.code.data.strip().lower(),
            Department.id != dept_id
        ).first()
        if existing:
            flash(f'Department code "{form.code.data}" is already used.', 'danger')
        else:
            dept.code = form.code.data.strip().upper()
            dept.name = form.name.data.strip()
            dept.description = form.description.data.strip() if form.description.data else None
            log_action(current_user.id, 'update', 'department', dept.id, f'Updated dept {dept.code}')
            db.session.commit()
            flash('Department updated.', 'success')
            return redirect(url_for('academic.departments'))
    return render_template('academic/dept_form.html', form=form, title='Edit Department', dept=dept)


# ---- Programs ----

@academic_bp.route('/programs')
@login_required
@admin_required
def programs():
    progs = Program.query.order_by(Program.name).all()
    return render_template('academic/programs.html', progs=progs)


@academic_bp.route('/programs/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_program():
    form = ProgramForm()
    form.department_id.choices = [
        (d.id, d.name) for d in Department.query.filter_by(active=True).order_by(Department.name).all()
    ]
    if form.validate_on_submit():
        existing = Program.query.filter(
            db.func.lower(Program.code) == form.code.data.strip().lower()
        ).first()
        if existing:
            flash(f'Program code "{form.code.data}" already exists.', 'danger')
        else:
            prog = Program(
                code=form.code.data.strip().upper(),
                name=form.name.data.strip(),
                department_id=form.department_id.data,
                duration_years=form.duration_years.data,
            )
            db.session.add(prog)
            db.session.flush()
            log_action(current_user.id, 'create', 'program', prog.id, f'Created program {prog.code}')
            db.session.commit()
            flash(f'Program "{prog.name}" created.', 'success')
            return redirect(url_for('academic.programs'))
    return render_template('academic/program_form.html', form=form, title='Add Program')


# ---- Academic Years ----

@academic_bp.route('/years')
@login_required
@admin_required
def academic_years():
    years = AcademicYear.query.order_by(AcademicYear.start_date.desc()).all()
    return render_template('academic/years.html', years=years)


@academic_bp.route('/years/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_academic_year():
    form = AcademicYearForm()
    if form.validate_on_submit():
        existing = AcademicYear.query.filter_by(label=form.label.data.strip()).first()
        if existing:
            flash(f'Academic year "{form.label.data}" already exists.', 'danger')
        else:
            year = AcademicYear(
                label=form.label.data.strip(),
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                active=form.active.data,
            )
            db.session.add(year)
            db.session.commit()
            flash(f'Academic year "{year.label}" created.', 'success')
            return redirect(url_for('academic.academic_years'))
    return render_template('academic/year_form.html', form=form, title='Add Academic Year')


# ---- Sections ----

@academic_bp.route('/sections')
@login_required
@admin_required
def sections():
    sect_list = Section.query.order_by(Section.program_id, Section.semester, Section.section_name).all()
    return render_template('academic/sections.html', sections=sect_list)


@academic_bp.route('/sections/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_section():
    form = SectionForm()
    form.program_id.choices = [
        (p.id, p.name) for p in Program.query.filter_by(active=True).order_by(Program.name).all()
    ]
    form.academic_year_id.choices = [
        (y.id, y.label) for y in AcademicYear.query.order_by(AcademicYear.start_date.desc()).all()
    ]
    if form.validate_on_submit():
        section = Section(
            program_id=form.program_id.data,
            academic_year_id=form.academic_year_id.data,
            semester=form.semester.data,
            section_name=form.section_name.data.strip().upper(),
        )
        db.session.add(section)
        try:
            db.session.commit()
            flash('Section created.', 'success')
            return redirect(url_for('academic.sections'))
        except Exception:
            db.session.rollback()
            flash('That section already exists for the selected program, year, and semester.', 'danger')
    return render_template('academic/section_form.html', form=form, title='Add Section')


# ---- Subjects ----

@academic_bp.route('/subjects')
@login_required
@admin_required
def subjects():
    subj_list = Subject.query.order_by(Subject.code).all()
    return render_template('academic/subjects.html', subjects=subj_list)


@academic_bp.route('/subjects/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_subject():
    form = SubjectForm()
    form.program_id.choices = [
        (p.id, p.name) for p in Program.query.filter_by(active=True).order_by(Program.name).all()
    ]
    if form.validate_on_submit():
        existing = Subject.query.filter(
            db.func.lower(Subject.code) == form.code.data.strip().lower()
        ).first()
        if existing:
            flash(f'Subject code "{form.code.data}" already exists.', 'danger')
        else:
            subj = Subject(
                code=form.code.data.strip().upper(),
                title=form.title.data.strip(),
                program_id=form.program_id.data,
                semester=form.semester.data if form.semester.data else None,
                credits=form.credits.data,
            )
            db.session.add(subj)
            db.session.commit()
            flash(f'Subject "{subj.title}" created.', 'success')
            return redirect(url_for('academic.subjects'))
    return render_template('academic/subject_form.html', form=form, title='Add Subject')


# ---- Super Admin Delete Routes ----

@academic_bp.route('/departments/<int:dept_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    if dept.programs.count() > 0:
        flash(f'Cannot delete department "{dept.name}" because it still has associated programs. Please delete or reassign them first.', 'danger')
        return redirect(url_for('academic.departments'))
    if dept.faculty_members.count() > 0:
        flash(f'Cannot delete department "{dept.name}" because it still has associated faculty members.', 'danger')
        return redirect(url_for('academic.departments'))
    
    code = dept.code
    name = dept.name
    log_action(current_user.id, 'delete', 'department', dept.id, f'Deleted department {code} ({name})')
    db.session.delete(dept)
    db.session.commit()
    flash(f'Department "{name}" ({code}) has been deleted.', 'success')
    return redirect(url_for('academic.departments'))


@academic_bp.route('/programs/<int:prog_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_program(prog_id):
    prog = Program.query.get_or_404(prog_id)
    if prog.sections.count() > 0:
        flash(f'Cannot delete program "{prog.name}" because it has associated sections.', 'danger')
        return redirect(url_for('academic.programs'))
    if prog.subjects.count() > 0:
        flash(f'Cannot delete program "{prog.name}" because it has associated subjects.', 'danger')
        return redirect(url_for('academic.programs'))
    if prog.students.count() > 0:
        flash(f'Cannot delete program "{prog.name}" because it has enrolled students.', 'danger')
        return redirect(url_for('academic.programs'))
    
    code = prog.code
    name = prog.name
    log_action(current_user.id, 'delete', 'program', prog.id, f'Deleted program {code} ({name})')
    db.session.delete(prog)
    db.session.commit()
    flash(f'Program "{name}" ({code}) has been deleted.', 'success')
    return redirect(url_for('academic.programs'))


@academic_bp.route('/years/<int:year_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_academic_year(year_id):
    year = AcademicYear.query.get_or_404(year_id)
    if year.sections.count() > 0:
        flash(f'Cannot delete academic year "{year.label}" because sections are mapped to it.', 'danger')
        return redirect(url_for('academic.academic_years'))
    if year.faculty_assignments.count() > 0:
        flash(f'Cannot delete academic year "{year.label}" because faculty assignments exist for it.', 'danger')
        return redirect(url_for('academic.academic_years'))
    
    label = year.label
    log_action(current_user.id, 'delete', 'academic_year', year.id, f'Deleted academic year {label}')
    db.session.delete(year)
    db.session.commit()
    flash(f'Academic year "{label}" has been deleted.', 'success')
    return redirect(url_for('academic.academic_years'))


@academic_bp.route('/sections/<int:section_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)
    if section.enrollments.count() > 0:
        flash(f'Cannot delete section "{section.display_name}" because students are currently enrolled in it. Reassign or remove enrollments first.', 'danger')
        return redirect(url_for('academic.sections'))
    
    # Cascade delete faculty assignments and attendance sessions
    for a in section.faculty_assignments.all():
        db.session.delete(a)
    for s in section.attendance_sessions.all():
        db.session.delete(s)
    
    display_name = section.display_name
    log_action(current_user.id, 'delete', 'section', section.id, f'Deleted section {display_name}')
    db.session.delete(section)
    db.session.commit()
    flash(f'Section "{display_name}" has been deleted.', 'success')
    return redirect(url_for('academic.sections'))


@academic_bp.route('/subjects/<int:subject_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Cascade delete any attendance sessions and faculty assignments for this subject
    for s in subject.attendance_sessions.all():
        db.session.delete(s)
    for a in subject.faculty_assignments.all():
        db.session.delete(a)
    
    code = subject.code
    title = subject.title
    log_action(current_user.id, 'delete', 'subject', subject.id, f'Deleted subject {code} ({title})')
    db.session.delete(subject)
    db.session.commit()
    flash(f'Subject "{code} - {title}" has been deleted.', 'success')
    return redirect(url_for('academic.subjects'))
