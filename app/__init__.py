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

            # Ensure default super admin exists
            sa_role = Role.query.filter_by(name='super_admin').first()
            if sa_role:
                for uname in ['admin', 'superadmin']:
                    if not User.query.filter_by(username=uname).first():
                        u = User(username=uname, email=f'{uname}@college.edu', role_id=sa_role.id, active=True)
                        u.set_password('Admin@123')
                        db.session.add(u)
                db.session.commit()

            if not InstitutionSettings.query.first():
                db.session.add(InstitutionSettings(
                    institution_name=app.config.get('INSTITUTION_NAME', 'College Management System')
                ))
                db.session.commit()
        except Exception as ex:
            app.logger.warning(f'Auto-init DB skipped or failed: {ex}')

    return app



