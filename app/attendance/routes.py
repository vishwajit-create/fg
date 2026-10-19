from datetime import date, datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.models.faculty import Faculty, FacultyAssignment
from app.models.student import Student, Enrollment
from app.models.academic import Section, Subject
from app.utils.decorators import faculty_or_admin_required, admin_required
from app.utils.audit import log_action

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('/')
@login_required
@faculty_or_admin_required
def index():
    """Show the register selection form."""
    # Faculty sees only their assignments; admins see all
    if current_user.is_admin() or current_user.is_dept_head():
        assignments = FacultyAssignment.query.all()
    else:
        faculty = Faculty.query.filter_by(
            user_account=None
        ).first()  # fallback
        if current_user.faculty_profile:
            assignments = FacultyAssignment.query.filter_by(
                faculty_id=current_user.faculty_profile.id
            ).all()
        else:
            flash('No teaching assignments linked to your account. Please contact an administrator.', 'warning')
            assignments = []

    recent = (
        AttendanceSession.query
        .order_by(AttendanceSession.session_date.desc(), AttendanceSession.created_at.desc())
        .limit(20)
        .all()
    )
    return render_template('attendance/index.html', assignments=assignments, recent=recent, today=date.today())



@attendance_bp.route('/open', methods=['GET', 'POST'])
@login_required
@faculty_or_admin_required
def open_register():
    """Open or create a register for a section/subject/date."""
    assignment_id = request.args.get('assignment_id', type=int)
    session_date_str = request.args.get('session_date', str(date.today()))
    session_label = request.args.get('session_label', '1')

    try:
        session_date = date.fromisoformat(session_date_str)
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('attendance.index'))

    if assignment_id:
        assignment = FacultyAssignment.query.get_or_404(assignment_id)
    else:
        flash('Please select a teaching assignment.', 'warning')
        return redirect(url_for('attendance.index'))

    # Security: faculty can only open their own assignments
    if current_user.is_faculty():
        if not current_user.faculty_profile or assignment.faculty_id != current_user.faculty_profile.id:
            flash('You are not authorised to open this register.', 'danger')
            return redirect(url_for('attendance.index'))

    # Find or create the attendance session
    session = AttendanceSession.query.filter_by(
        section_id=assignment.section_id,
        subject_id=assignment.subject_id,
        session_date=session_date,
        session_label=session_label,
    ).first()

    if not session:
        session = AttendanceSession(
            section_id=assignment.section_id,
            subject_id=assignment.subject_id,
            faculty_id=assignment.faculty_id,
            session_date=session_date,
            session_label=session_label,
            status='draft',
        )
        db.session.add(session)
        db.session.commit()

    return redirect(url_for('attendance.mark', session_id=session.id))


@attendance_bp.route('/session/<int:session_id>/mark', methods=['GET', 'POST'])
@login_required
@faculty_or_admin_required
def mark(session_id):
    """Display and save the attendance register."""
    session = AttendanceSession.query.get_or_404(session_id)

    # Authorisation: faculty only for their sessions
    if current_user.is_faculty():
        if not current_user.faculty_profile or session.faculty_id != current_user.faculty_profile.id:
            flash('You are not authorised to mark this register.', 'danger')
            return redirect(url_for('attendance.index'))

    if session.status == 'locked' and not current_user.is_admin():
        flash('This register is locked. Contact an administrator to make corrections.', 'warning')
        return redirect(url_for('attendance.view', session_id=session_id))

    # Fetch students eligible to attend:
    # 1. Directly enrolled in this section
    # 2. Or registered under the same program or department (e.g. CSE branch students can attend any CSE class/program)
    enrolled_student_ids = [
        e.student_id for e in Enrollment.query.filter_by(section_id=session.section_id, status='active').all()
    ]
    
    # Get program and department IDs for the current class/section
    prog_id = session.section.program_id if session.section else None
    dept_id = session.section.program.department_id if session.section and session.section.program else None

    # Query students: directly enrolled, or in same program, or in same branch/department
    candidate_query = Student.query.filter(Student.status == 'active')
    
    conditions = []
    if enrolled_student_ids:
        conditions.append(Student.id.in_(enrolled_student_ids))
    if prog_id:
        conditions.append(Student.program_id == prog_id)
    if dept_id:
        conditions.append(Student.program.has(department_id=dept_id))
    
    if conditions:
        students = candidate_query.filter(db.or_(*conditions)).order_by(Student.roll_number).all()
    else:
        students = candidate_query.order_by(Student.roll_number).all()

    # Fetch existing records
    existing = {r.student_id: r for r in session.records.all()}

    if request.method == 'POST':
        if session.status == 'submitted' and not current_user.is_admin():
            flash('Only administrators can correct a submitted register.', 'danger')
            return redirect(url_for('attendance.view', session_id=session_id))

        is_correction = session.status == 'submitted'
        correction_reason = request.form.get('correction_reason', '').strip()

        with db.session.begin_nested():
            for student in students:
                status = request.form.get(f'status_{student.id}', '').strip()
                if status not in ('present', 'absent', 'leave'):
                    flash(f'Invalid status for {student.full_name}.', 'danger')
                    return render_template('attendance/mark.html', session=session,
                                           students=students, existing=existing)

                record = existing.get(student.id)
                if record:
                    if is_correction:
                        old_status = record.status
                        record.correction_note = f'Changed from {old_status} to {status}. Reason: {correction_reason}'
                    record.status = status
                    record.marked_by = current_user.id
                    record.marked_at = datetime.now(timezone.utc)
                else:
                    record = AttendanceRecord(
                        session_id=session.id,
                        student_id=student.id,
                        status=status,
                        marked_by=current_user.id,
                    )
                    db.session.add(record)

            if 'submit' in request.form:
                session.status = 'submitted'
                session.submitted_at = datetime.now(timezone.utc)

            log_action(current_user.id, 'submit_attendance' if 'submit' in request.form else 'save_draft',
                       'attendance_session', session.id,
                       f'Session {session.session_date} section={session.section_id}')

        db.session.commit()

        if 'submit' in request.form:
            flash('Attendance register submitted successfully.', 'success')
            return redirect(url_for('attendance.view', session_id=session_id))
        else:
            flash('Draft saved.', 'info')
            return redirect(url_for('attendance.mark', session_id=session_id))

    return render_template('attendance/mark.html', session=session,
                           students=students, existing=existing)


@attendance_bp.route('/session/<int:session_id>/view')
@login_required
@faculty_or_admin_required
def view(session_id):
    session = AttendanceSession.query.get_or_404(session_id)
    records = {r.student_id: r for r in session.records.all()}
    return render_template('attendance/view.html', session=session, records=records)


@attendance_bp.route('/session/<int:session_id>/lock', methods=['POST'])
@login_required
@admin_required
def lock_session(session_id):
    session = AttendanceSession.query.get_or_404(session_id)
    session.status = 'locked'
    log_action(current_user.id, 'lock', 'attendance_session', session.id,
               f'Locked session {session.session_date}')
    db.session.commit()
    flash('Register locked.', 'success')
    return redirect(url_for('attendance.view', session_id=session_id))
