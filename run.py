import os
import click
from app import create_app
from app.extensions import db
from app.models import User, Role, Department, Program, AcademicYear, Section, Subject
from app.models.audit import InstitutionSettings

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.cli.command('seed-db')
@click.option('--admin-password', prompt=True, hide_input=True,
               confirmation_prompt=True, help='Password for the initial admin account.')
def seed_db(admin_password):
    """Create default roles and the first super-admin account."""
    with app.app_context():
        db.create_all()

        # Roles
        role_defs = [
            ('super_admin', 'Full system access'),
            ('college_admin', 'College administrator / registrar'),
            ('dept_head', 'Department head'),
            ('faculty', 'Teaching faculty member'),
            ('auditor', 'Read-only audit access'),
        ]
        for name, desc in role_defs:
            if not Role.query.filter_by(name=name).first():
                db.session.add(Role(name=name, description=desc))
        db.session.commit()

        # Super admin
        if not User.query.filter_by(username='admin').first():
            admin_role = Role.query.filter_by(name='super_admin').first()
            admin = User(
                username='admin',
                email='admin@college.local',
                role_id=admin_role.id,
                active=True,
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            click.echo('Super-admin account created: username=admin')
        else:
            click.echo('Admin account already exists — skipped.')

        # Default institution settings
        if not InstitutionSettings.query.first():
            db.session.add(InstitutionSettings(
                institution_name=app.config.get('INSTITUTION_NAME', 'My College'),
            ))
            db.session.commit()

        click.echo('Database seeded successfully.')


if __name__ == '__main__':
    app.run()
