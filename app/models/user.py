from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    users = db.relationship('User', back_populates='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login_at = db.Column(db.DateTime)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)

    role = db.relationship('Role', back_populates='users')
    faculty_profile = db.relationship('Faculty', back_populates='user_account', foreign_keys=[faculty_id])
    audit_logs = db.relationship('AuditLog', back_populates='actor', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, *role_names):
        return self.role and self.role.name in role_names

    def is_admin(self):
        return self.has_role('super_admin', 'college_admin')

    def is_super_admin(self):
        return self.has_role('super_admin')

    def is_faculty(self):
        return self.has_role('faculty')

    def is_dept_head(self):
        return self.has_role('dept_head')

    @property
    def is_active(self):
        return self.active

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
