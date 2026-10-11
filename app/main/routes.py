from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.academic import Department
from app.models.attendance import AttendanceSession

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()

    active_students = Student.query.filter_by(status='active').count()
    active_faculty = Faculty.query.filter_by(status='active').count()
    departments = Department.query.filter_by(active=True).count()
    todays_sessions = AttendanceSession.query.filter_by(session_date=today).count()
    submitted_today = AttendanceSession.query.filter_by(session_date=today, status='submitted').count()

    recent_sessions = (
        AttendanceSession.query
        .order_by(AttendanceSession.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        'dashboard.html',
        active_students=active_students,
        active_faculty=active_faculty,
        departments=departments,
        todays_sessions=todays_sessions,
        submitted_today=submitted_today,
        recent_sessions=recent_sessions,
        now=today,
    )

