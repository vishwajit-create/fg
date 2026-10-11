from datetime import datetime, timezone
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # login, create, update, archive, etc.
    entity_type = db.Column(db.String(50))  # student, faculty, attendance_session, etc.
    entity_id = db.Column(db.Integer)
    change_summary = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    actor = db.relationship('User', back_populates='audit_logs')

    def __repr__(self):
        return f'<AuditLog {self.action} on {self.entity_type}:{self.entity_id}>'


class InstitutionSettings(db.Model):
    __tablename__ = 'institution_settings'

    id = db.Column(db.Integer, primary_key=True)
    institution_name = db.Column(db.String(200), nullable=False, default='My College')
    short_name = db.Column(db.String(50))
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    timezone = db.Column(db.String(50), default='Asia/Kolkata')
    attendance_edit_window_hours = db.Column(db.Integer, default=24)
    leave_counts_in_denominator = db.Column(db.Boolean, default=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=True)

    academic_year = db.relationship('AcademicYear')
