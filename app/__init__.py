import os
from flask import Flask
from app.config import config
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config.get(config_name, config['default']))

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.students.routes import students_bp
    from app.faculty.routes import faculty_bp
    from app.academic.routes import academic_bp
    from app.attendance.routes import attendance_bp
    from app.reports.routes import reports_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(academic_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)

    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)

    # Inject globals into templates
    from app.context_processors import register_context_processors
    register_context_processors(app)

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    # ProxyFix for reverse proxies (Render, Nginx, etc.)
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Automatically ensure tables and default roles/admin exist on startup
    with app.app_context():
        try:
            from app.models import Role, User, InstitutionSettings
            db.create_all()

            # --- Roles ---
            for r_name, desc in [
                ('super_admin', 'Full system access'),
                ('college_admin', 'College administrator / registrar'),
                ('dept_head', 'Department head'),
                ('faculty', 'Teaching faculty member'),
                ('auditor', 'Read-only audit access')
            ]:
                if not Role.query.filter_by(name=r_name).first():
                    db.session.add(Role(name=r_name, description=desc))
            db.session.commit()

            # --- Default super admin users ---
            sa_role = Role.query.filter_by(name='super_admin').first()
            if sa_role:
                for uname in ['admin', 'superadmin']:
                    if not User.query.filter_by(username=uname).first():
                        u = User(username=uname, email=f'{uname}@college.edu',
                                 role_id=sa_role.id, active=True)
                        u.set_password('Admin@123')
                        db.session.add(u)
                db.session.commit()

            # --- Institution settings ---
            if not InstitutionSettings.query.first():
                db.session.add(InstitutionSettings(
                    institution_name='Shri Phanishwar Nath Renu Engineering College, Araria'
                ))
            else:
                settings = InstitutionSettings.query.first()
                if settings.institution_name in ('College Management System', 'CSFMS'):
                    settings.institution_name = 'Shri Phanishwar Nath Renu Engineering College, Araria'
            db.session.commit()

            # ----------------------------------------------------------------
            # SEED REAL COLLEGE DATA  (idempotent — safe to re-run)
            # ----------------------------------------------------------------
            from datetime import date
            from app.models.academic import Department, Program, AcademicYear, Section, Subject
            from app.models.faculty import Faculty, FacultyAssignment

            # Department
            dept = Department.query.filter_by(code='CSE').first()
            if not dept:
                dept = Department(code='CSE',
                                  name='Computer Science and Engineering',
                                  active=True)
                db.session.add(dept)
                db.session.flush()

            # Program
            prog = Program.query.filter_by(code='BTECH-CSE').first()
            if not prog:
                prog = Program(code='BTECH-CSE',
                               name='B.Tech - Computer Science and Engineering',
                               duration_years=4,
                               department_id=dept.id,
                               active=True)
                db.session.add(prog)
                db.session.flush()

            # Academic Year
            ay = AcademicYear.query.filter_by(label='2025-26').first()
            if not ay:
                ay = AcademicYear(label='2025-26',
                                  start_date=date(2025, 7, 1),
                                  end_date=date(2026, 6, 30),
                                  active=True)
                db.session.add(ay)
                db.session.flush()
            else:
                if not ay.active:
                    ay.active = True

            # Section — 4th Sem CSE-B
            sec = Section.query.filter_by(
                program_id=prog.id,
                academic_year_id=ay.id,
                semester=4,
                section_name='B'
            ).first()
            if not sec:
                sec = Section(program_id=prog.id,
                              academic_year_id=ay.id,
                              semester=4,
                              section_name='B',
                              active=True)
                db.session.add(sec)
                db.session.flush()

            # Faculty members
            faculty_data = [
                ('FAC001', 'Prof. Shweta Kumari',      'Asst. Professor, CSE'),
                ('FAC002', 'Prof. Agam Kumar',          'Asst. Professor, CSE'),
                ('FAC003', 'Prof. Krishnanand Mishra',  'Asst. Professor, CSE'),
                ('FAC004', 'Prof. Abnish Ranjan',       'Asst. Professor, CSE'),
                ('FAC005', 'Prof. Shauraya Ranjan',     'Asst. Professor, CSE'),
                ('FAC006', 'Mr. Swagata Chakraborty',   'GAP English'),
                ('FAC007', 'Mr. Hira Kumar Thakur',     'Lab Assistant'),
            ]
            fac_map = {}  # employee_id -> Faculty object
            for emp_id, full_name, desig in faculty_data:
                fac = Faculty.query.filter_by(employee_id=emp_id).first()
                if not fac:
                    fac = Faculty(employee_id=emp_id,
                                  full_name=full_name,
                                  department_id=dept.id,
                                  designation=desig,
                                  status='active')
                    db.session.add(fac)
                    db.session.flush()
                fac_map[emp_id] = fac

            # Subjects
            subject_data = [
                ('105401',  'Computer Organization & Architecture',       4, 4),
                ('105402',  'Formal Language and Automata Theory',         4, 4),
                ('105403',  'Design and Analysis of Algorithms',           4, 4),
                ('105404',  'Database Management System',                  4, 4),
                ('105405',  'Effective Technical Communication',           3, 4),
                ('105406',  'Computer Networks',                           4, 4),
                ('105407',  'NPTEL-I',                                     2, 4),
                ('105401P', 'Computer Organization & Architecture Lab',    2, 4),
                ('105403P', 'Design and Analysis of Algorithms Lab',       2, 4),
                ('105404P', 'Database Management System Lab',              2, 4),
                ('105406P', 'Computer Networks Lab',                       2, 4),
            ]
            subj_map = {}  # code -> Subject object
            for code, title, credits, sem in subject_data:
                subj = Subject.query.filter_by(code=code).first()
                if not subj:
                    subj = Subject(code=code,
                                   title=title,
                                   program_id=prog.id,
                                   semester=sem,
                                   credits=credits,
                                   active=True)
                    db.session.add(subj)
                    db.session.flush()
                subj_map[code] = subj

            # Faculty Assignments (primary faculty + lab assistant where applicable)
            # Format: (subject_code, employee_id)
            assignments = [
                ('105401',  'FAC002'),   # COA  — Agam Kumar
                ('105402',  'FAC005'),   # TOC  — Shauraya Ranjan
                ('105403',  'FAC003'),   # DAA  — Krishnanand Mishra
                ('105404',  'FAC004'),   # DBMS — Abnish Ranjan
                ('105405',  'FAC006'),   # ETC  — Swagata Chakraborty
                ('105406',  'FAC001'),   # CN   — Shweta Kumari
                ('105407',  'FAC001'),   # NPTEL-I — Shweta Kumari
                # Lab subjects — primary prof
                ('105401P', 'FAC002'),   # COA Lab  — Agam Kumar
                ('105403P', 'FAC003'),   # DAA Lab  — Krishnanand Mishra
                ('105404P', 'FAC004'),   # DBMS Lab — Abnish Ranjan
                ('105406P', 'FAC001'),   # CN Lab   — Shweta Kumari
                # Lab subjects — Lab Assistant
                ('105401P', 'FAC007'),   # COA Lab  — Hira Kumar Thakur
                ('105403P', 'FAC007'),   # DAA Lab  — Hira Kumar Thakur
                ('105404P', 'FAC007'),   # DBMS Lab — Hira Kumar Thakur
                ('105406P', 'FAC007'),   # CN Lab   — Hira Kumar Thakur
            ]
            for subj_code, emp_id in assignments:
                fac_obj  = fac_map[emp_id]
                subj_obj = subj_map[subj_code]
                existing = FacultyAssignment.query.filter_by(
                    faculty_id=fac_obj.id,
                    section_id=sec.id,
                    subject_id=subj_obj.id,
                    academic_year_id=ay.id
                ).first()
                if not existing:
                    db.session.add(FacultyAssignment(
                        faculty_id=fac_obj.id,
                        section_id=sec.id,
                        subject_id=subj_obj.id,
                        academic_year_id=ay.id
                    ))

            db.session.commit()
            app.logger.info('CSFMS: seed data committed successfully.')

        except Exception as ex:
            db.session.rollback()
            app.logger.warning(f'Auto-init DB skipped or failed: {ex}')

    return app
