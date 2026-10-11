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
