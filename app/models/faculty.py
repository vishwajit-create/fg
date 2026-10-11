from datetime import datetime, timezone
from app.extensions import db


class Faculty(db.Model):
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(150), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    designation = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    qualification = db.Column(db.String(150))
    joining_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active', nullable=False)  # active, archived
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    department = db.relationship('Department', back_populates='faculty_members')
    assignments = db.relationship('FacultyAssignment', back_populates='faculty', lazy='dynamic')
    attendance_sessions = db.relationship('AttendanceSession', back_populates='faculty', lazy='dynamic')
    user_account = db.relationship('User', back_populates='faculty_profile', foreign_keys='User.faculty_id')

    def __repr__(self):
        return f'<Faculty {self.employee_id} {self.full_name}>'


class FacultyAssignment(db.Model):
    __tablename__ = 'faculty_assignments'

    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('faculty_id', 'section_id', 'subject_id', 'academic_year_id',
                            name='uq_faculty_assignment'),
    )

    faculty = db.relationship('Faculty', back_populates='assignments')
    section = db.relationship('Section', back_populates='faculty_assignments')
    subject = db.relationship('Subject', back_populates='faculty_assignments')
    academic_year = db.relationship('AcademicYear', back_populates='faculty_assignments')

    def __repr__(self):
        return f'<FacultyAssignment faculty={self.faculty_id} section={self.section_id} subject={self.subject_id}>'
