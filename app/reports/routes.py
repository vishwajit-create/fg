from datetime import date
from io import BytesIO
from flask import Blueprint, render_template, request, send_file, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.models.academic import Section, Subject, Program
from app.utils.decorators import faculty_or_admin_required
from app.utils.csv_export import generate_csv

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


def _parse_date(val, default):
    try:
        return date.fromisoformat(val) if val else default
    except ValueError:
        return default


@reports_bp.route('/')
@login_required
@faculty_or_admin_required
def index():
    return render_template('reports/index.html')


@reports_bp.route('/attendance')
@login_required
@faculty_or_admin_required
def attendance_report():
    today = date.today()
    start = _parse_date(request.args.get('start'), date(today.year, today.month, 1))
    end = _parse_date(request.args.get('end'), today)

    if end < start:
        end = start

    section_id = request.args.get('section_id', type=int)
    subject_id = request.args.get('subject_id', type=int)

    # Build query
    query = (
        db.session.query(
            Student.id,
            Student.roll_number,
            Student.full_name,
            func.count(AttendanceRecord.id).label('total_sessions'),
            func.sum(
                db.case((AttendanceRecord.status == 'present', 1), else_=0)
            ).label('present_count'),
        )
        .join(AttendanceRecord, AttendanceRecord.student_id == Student.id)
        .join(AttendanceSession, AttendanceSession.id == AttendanceRecord.session_id)
        .filter(
            AttendanceSession.session_date >= start,
            AttendanceSession.session_date <= end,
            AttendanceSession.status == 'submitted',
        )
    )

    if section_id:
        query = query.filter(AttendanceSession.section_id == section_id)
    if subject_id:
        query = query.filter(AttendanceSession.subject_id == subject_id)

    results = query.group_by(Student.id, Student.roll_number, Student.full_name).all()

    report_rows = []
    for row in results:
        pct = round(row.present_count / row.total_sessions * 100, 2) if row.total_sessions else None
        report_rows.append({
            'roll_number': row.roll_number,
            'full_name': row.full_name,
            'total_sessions': row.total_sessions,
            'present_count': row.present_count,
            'percentage': pct,
        })

    sections = Section.query.filter_by(active=True).order_by(Section.section_name).all()
    subjects = Subject.query.filter_by(active=True).order_by(Subject.code).all()

    export = request.args.get('export')
    if export == 'csv':
        headers = ['Roll Number', 'Student Name', 'Total Sessions', 'Present', 'Attendance %']
        rows = [
            [r['roll_number'], r['full_name'], r['total_sessions'],
             r['present_count'], r['percentage'] if r['percentage'] is not None else 'N/A']
            for r in report_rows
        ]
        csv_buf = generate_csv(headers, rows)
        return send_file(csv_buf, mimetype='text/csv',
                         as_attachment=True,
                         download_name=f'attendance_{start}_{end}.csv')

    return render_template(
        'reports/attendance.html',
        report_rows=report_rows,
        start=start, end=end,
        sections=sections, subjects=subjects,
        section_id=section_id, subject_id=subject_id,
    )


@reports_bp.route('/students')
@login_required
@faculty_or_admin_required
def students_report():
    program_id = request.args.get('program_id', type=int)
    status = request.args.get('status', 'active')

    query = Student.query
    if status != 'all':
        query = query.filter_by(status=status)
    if program_id:
        query = query.filter_by(program_id=program_id)

    students = query.order_by(Student.roll_number).all()
    programs = Program.query.filter_by(active=True).order_by(Program.name).all()

    export = request.args.get('export')
    if export == 'csv':
        headers = ['Roll Number', 'Full Name', 'Program', 'Email', 'Phone', 'Status']
        rows = [
            [s.roll_number, s.full_name,
             s.program.name if s.program else '',
             s.email or '', s.phone or '', s.status]
            for s in students
        ]
        csv_buf = generate_csv(headers, rows)
        return send_file(csv_buf, mimetype='text/csv', as_attachment=True,
                         download_name='students_report.csv')

    return render_template('reports/students.html', students=students,
                           programs=programs, program_id=program_id, status=status)
