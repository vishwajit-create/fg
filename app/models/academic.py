from datetime import datetime, timezone
from app.extensions import db


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    programs = db.relationship('Program', back_populates='department', lazy='dynamic')
    faculty_members = db.relationship('Faculty', back_populates='department', lazy='dynamic')

    def __repr__(self):
        return f'<Department {self.code}>'


class Program(db.Model):
    __tablename__ = 'programs'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    duration_years = db.Column(db.Integer, default=3)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    department = db.relationship('Department', back_populates='programs')
    sections = db.relationship('Section', back_populates='program', lazy='dynamic')
    subjects = db.relationship('Subject', back_populates='program', lazy='dynamic')
    students = db.relationship('Student', back_populates='program', lazy='dynamic')

    def __repr__(self):
        return f'<Program {self.code}>'


class AcademicYear(db.Model):
    __tablename__ = 'academic_years'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(20), unique=True, nullable=False)  # e.g. 2024-25
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    sections = db.relationship('Section', back_populates='academic_year', lazy='dynamic')
    faculty_assignments = db.relationship('FacultyAssignment', back_populates='academic_year', lazy='dynamic')

    def __repr__(self):
        return f'<AcademicYear {self.label}>'


class Section(db.Model):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)  # 1-8
    section_name = db.Column(db.String(20), nullable=False)  # A, B, C
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('program_id', 'academic_year_id', 'semester', 'section_name',
                            name='uq_section'),
    )

    program = db.relationship('Program', back_populates='sections')
    academic_year = db.relationship('AcademicYear', back_populates='sections')
    enrollments = db.relationship('Enrollment', back_populates='section', lazy='dynamic')
    faculty_assignments = db.relationship('FacultyAssignment', back_populates='section', lazy='dynamic')
    attendance_sessions = db.relationship('AttendanceSession', back_populates='section', lazy='dynamic')

    @property
    def display_name(self):
        return f'{self.program.code} Sem-{self.semester} {self.section_name}'

    def __repr__(self):
        return f'<Section {self.display_name}>'


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=True)  # optional: links to specific semester
    credits = db.Column(db.Integer, default=3)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    program = db.relationship('Program', back_populates='subjects')
    faculty_assignments = db.relationship('FacultyAssignment', back_populates='subject', lazy='dynamic')
    attendance_sessions = db.relationship('AttendanceSession', back_populates='subject', lazy='dynamic')

    def __repr__(self):
        return f'<Subject {self.code}>'
