from datetime import datetime, timezone
from app.extensions import db


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(150), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=True)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    admission_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)  # active, archived
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    program = db.relationship('Program', back_populates='students')
    section = db.relationship('Section')
    enrollments = db.relationship('Enrollment', back_populates='student', lazy='dynamic')
    attendance_records = db.relationship('AttendanceRecord', back_populates='student', lazy='dynamic')

    def __repr__(self):
        return f'<Student {self.roll_number} {self.full_name}>'


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active', nullable=False)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'section_id', name='uq_enrollment'),
    )

    student = db.relationship('Student', back_populates='enrollments')
    section = db.relationship('Section', back_populates='enrollments')

    def __repr__(self):
        return f'<Enrollment student={self.student_id} section={self.section_id}>'
