from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.utils.audit import log_action
from app.auth.forms import LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.username.data)
        ).first()

        if user and user.check_password(form.password.data) and user.active:
            login_user(user, remember=False)
            user.last_login_at = datetime.now(timezone.utc)
            log_action(user.id, 'login')
            db.session.commit()
            next_page = request.args.get('next')
            flash('Welcome back, ' + user.username + '.', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            log_action(None, 'login_failed', change_summary=f'username={form.username.data}')
            db.session.commit()
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    log_action(current_user.id, 'logout')
    db.session.commit()
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('auth.login'))
