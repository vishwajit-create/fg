from datetime import datetime, timezone
from app.extensions import db


class AttendanceSession(db.Model):
    __tablename__ = 'attendance_sessions'

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, index=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False, index=True)
    session_label = db.Column(db.String(20), default='1')  # period/session identifier
    status = db.Column(db.String(20), default='draft', nullable=False)  # draft, submitted, locked
    submitted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('section_id', 'subject_id', 'session_date', 'session_label',
                            name='uq_attendance_session'),
    )

    section = db.relationship('Section', back_populates='attendance_sessions')
    subject = db.relationship('Subject', back_populates='attendance_sessions')
    faculty = db.relationship('Faculty', back_populates='attendance_sessions')
    records = db.relationship('AttendanceRecord', back_populates='session',
                              cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<AttendanceSession {self.session_date} section={self.section_id} subject={self.subject_id}>'


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id'), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    status = db.Column(db.String(10), nullable=False)  # present, absent, leave
    marked_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    marked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    correction_note = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint('session_id', 'student_id', name='uq_attendance_record'),
    )

    session = db.relationship('AttendanceSession', back_populates='records')
    student = db.relationship('Student', back_populates='attendance_records')
    marker = db.relationship('User', foreign_keys=[marked_by])

    def __repr__(self):
        return f'<AttendanceRecord session={self.session_id} student={self.student_id} status={self.status}>'
