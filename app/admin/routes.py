import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User, Role
from app.models.faculty import Faculty
from app.models.audit import AuditLog
from app.utils.decorators import admin_required, roles_required
from app.utils.audit import log_action
from app.admin.forms import UserCreateForm, UserEditForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    user_list = User.query.order_by(User.username).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=user_list)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = UserCreateForm()
    form.role_id.choices = [(r.id, r.name.replace('_', ' ').title())
                             for r in Role.query.order_by(Role.name).all()]
    form.faculty_id.choices = [(0, '-- Not Linked --')] + [
        (f.id, f'{f.full_name} ({f.employee_id})')
        for f in Faculty.query.filter_by(status='active').order_by(Faculty.full_name).all()
    ]

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data.strip()).first():
            flash('Username already taken.', 'danger')
        elif User.query.filter_by(email=form.email.data.strip()).first():
            flash('Email already registered.', 'danger')
        else:
            user = User(
                username=form.username.data.strip(),
                email=form.email.data.strip(),
                role_id=form.role_id.data,
                faculty_id=form.faculty_id.data if form.faculty_id.data else None,
                active=True,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()
            log_action(current_user.id, 'create_user', 'user', user.id,
                       f'Created user {user.username}')
            db.session.commit()
            flash(f'User "{user.username}" created.', 'success')
            return redirect(url_for('admin.users'))

    return render_template('admin/user_form.html', form=form, title='Add User')


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    form.role_id.choices = [(r.id, r.name.replace('_', ' ').title())
                             for r in Role.query.order_by(Role.name).all()]

    if form.validate_on_submit():
        user.role_id = form.role_id.data
        user.active = form.active.data
        log_action(current_user.id, 'update_user', 'user', user.id,
                   f'Updated user {user.username} active={user.active}')
        db.session.commit()
        flash('User updated.', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_form.html', form=form, title='Edit User', user=user)


def _generate_temp_password():
    """Generate a readable, cryptographically random 10-char temporary password."""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'
    digits = '23456789'
    body = ''.join(secrets.choice(chars) for _ in range(7))
    suffix = ''.join(secrets.choice(digits) for _ in range(2))
    return f'{body}@{suffix}'


def provision_unlinked_faculty(actor_user_id=None):
    """Create user accounts for all active faculty/staff without an existing account.

    Returns a list of dicts containing generated credentials (plaintext temp_password
    is only available at creation time).
    """
    faculty_role = Role.query.filter_by(name='faculty').first()
    if not faculty_role:
        return []

    linked_faculty_ids = {
        u.faculty_id for u in User.query.filter(User.faculty_id.isnot(None)).all()
    }
    unlinked = (
        Faculty.query
        .filter_by(status='active')
        .order_by(Faculty.employee_id)
        .all()
    )

    provisioned = []
    for member in unlinked:
        if member.id in linked_faculty_ids:
            continue

        base_username = ''.join(c for c in member.employee_id.strip().lower() if c.isalnum() or c in '._-')
        if not base_username:
            base_username = f'fac{member.id}'

        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f'{base_username}_{counter}'
            counter += 1

        email = member.email.strip().lower() if member.email else f'{username}@pending.local'
        if User.query.filter(db.func.lower(User.email) == email).first():
            email = f'{username}@pending.local'

        temp_password = _generate_temp_password()
        user = User(
            username=username,
            email=email,
            role_id=faculty_role.id,
            faculty_id=member.id,
            active=True,
            must_change_password=True,
        )
        user.set_password(temp_password)
        db.session.add(user)
        provisioned.append({
            'employee_id': member.employee_id,
            'full_name': member.full_name,
            'designation': member.designation or 'Staff',
            'username': username,
            'temp_password': temp_password,
            'email': email,
        })

    if provisioned:
        db.session.flush()
        log_action(
            actor_user_id,
            'batch_provision_faculty',
            'user',
            None,
            f'Provisioned {len(provisioned)} faculty/staff user account(s)',
        )
        db.session.commit()

    return provisioned


@admin_bp.route('/users/provision-faculty', methods=['POST'])
@login_required
@admin_required
def provision_faculty():
    provisioned = provision_unlinked_faculty(actor_user_id=current_user.id)
    if not provisioned:
        flash('All active teachers and lab assistants already have user accounts.', 'info')
        return redirect(url_for('admin.users'))
    flash(f'Created {len(provisioned)} faculty/staff account(s). Save these credentials securely.', 'success')
    return render_template('admin/provision_result.html', provisioned=provisioned)


@admin_bp.route('/audit')
@login_required
@roles_required('super_admin', 'college_admin')
def audit_log():
    page = request.args.get('page', 1, type=int)
    logs = (
        AuditLog.query
        .order_by(AuditLog.created_at.desc())
        .paginate(page=page, per_page=50, error_out=False)
    )
    return render_template('admin/audit_log.html', logs=logs)
