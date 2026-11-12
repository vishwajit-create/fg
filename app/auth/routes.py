import secrets
from datetime import datetime, timedelta, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.user import User
from app.utils.audit import log_action
from app.utils.email import send_otp_email
from app.auth.forms import LoginForm, ProfileForm, ForgotPasswordForm, ResetPasswordOTPForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.before_app_request
def enforce_profile_setup():
    """Force newly provisioned users to set a real email and personal password."""
    if not current_user.is_authenticated:
        return None
    if not current_user.needs_profile_setup():
        return None
    allowed_endpoints = {'auth.profile', 'auth.logout', 'static'}
    if request.endpoint in allowed_endpoints or (request.endpoint and request.endpoint.startswith('static')):
        return None
    flash('Please set your email address and change your temporary password to continue.', 'warning')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data.strip()) | (User.email == form.username.data.strip())
        ).first()

        if user and user.check_password(form.password.data) and user.active:
            login_user(user, remember=False)
            user.last_login_at = datetime.now(timezone.utc)
            log_action(user.id, 'login')
            db.session.commit()
            if user.needs_profile_setup():
                flash('Welcome! Please add your email address and set a new personal password.', 'warning')
                return redirect(url_for('auth.profile'))
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


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if request.method == 'GET':
        form.email.data = '' if current_user.has_pending_email() else current_user.email

    if form.validate_on_submit():
        new_email = form.email.data.strip().lower()
        if new_email.endswith('@pending.local'):
            flash('Please enter a valid personal or college email address.', 'danger')
            return render_template('auth/profile.html', form=form)

        existing_email = User.query.filter(
            db.func.lower(User.email) == new_email,
            User.id != current_user.id
        ).first()
        if existing_email:
            flash('That email address is already registered to another account.', 'danger')
            return render_template('auth/profile.html', form=form)

        wants_password_change = bool(form.new_password.data)
        if current_user.must_change_password and not wants_password_change:
            flash('You must set a new personal password before continuing.', 'danger')
            return render_template('auth/profile.html', form=form)

        if wants_password_change:
            if not form.current_password.data or not current_user.check_password(form.current_password.data):
                flash('Current password is incorrect.', 'danger')
                return render_template('auth/profile.html', form=form)
            current_user.set_password(form.new_password.data)
            current_user.must_change_password = False

        current_user.email = new_email
        if current_user.faculty_profile:
            current_user.faculty_profile.email = new_email

        log_action(current_user.id, 'update_profile', 'user', current_user.id,
                   f'Updated profile email={new_email}, password_changed={wants_password_change}')
        db.session.commit()
        flash('Your profile and security settings have been saved.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/profile.html', form=form)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        ident = form.identifier.data.strip()
        user = User.query.filter(
            (User.username == ident) | (db.func.lower(User.email) == ident.lower())
        ).first()

        if not user or not user.active:
            flash('If an active account with that username or email exists, an OTP has been sent.', 'info')
            return redirect(url_for('auth.reset_password', identifier=ident))

        if user.has_pending_email():
            flash('No email address is registered on this account yet. Please sign in with your temporary password or contact the administrator.', 'warning')
            return redirect(url_for('auth.login'))

        otp_code = f'{secrets.randbelow(900000) + 100000}'
        user.otp_code_hash = generate_password_hash(otp_code)
        user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        user.otp_attempts = 0
        db.session.commit()

        sent, err = send_otp_email(user.email, user.username, otp_code)
        if not sent:
            flash(err or 'Unable to send OTP email right now.', 'danger')
            return render_template('auth/forgot_password.html', form=form)

        log_action(user.id, 'otp_requested', 'user', user.id, f'OTP sent to {user.email}')
        db.session.commit()
        flash(f'A 6-digit OTP has been sent to your registered email ({user.email}). It is valid for 10 minutes.', 'success')
        return redirect(url_for('auth.reset_password', identifier=user.username))

    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = ResetPasswordOTPForm()
    if request.method == 'GET' and request.args.get('identifier'):
        form.identifier.data = request.args.get('identifier', '').strip()

    if form.validate_on_submit():
        ident = form.identifier.data.strip()
        user = User.query.filter(
            (User.username == ident) | (db.func.lower(User.email) == ident.lower())
        ).first()

        if not user or not user.otp_code_hash or not user.otp_expires_at:
            flash('Invalid or expired OTP request. Please request a new OTP.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        expires_at = user.otp_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) > expires_at:
            user.otp_code_hash = None
            user.otp_expires_at = None
            user.otp_attempts = 0
            db.session.commit()
            flash('Your OTP has expired. Please request a new one.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        if user.otp_attempts >= 5:
            user.otp_code_hash = None
            user.otp_expires_at = None
            db.session.commit()
            flash('Too many invalid OTP attempts. Please request a new OTP.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        if not check_password_hash(user.otp_code_hash, form.otp.data.strip()):
            user.otp_attempts += 1
            db.session.commit()
            remaining = max(0, 5 - user.otp_attempts)
            flash(f'Invalid OTP code. {remaining} attempt(s) remaining.', 'danger')
            return render_template('auth/reset_password.html', form=form)

        user.set_password(form.new_password.data)
        user.must_change_password = False
        user.otp_code_hash = None
        user.otp_expires_at = None
        user.otp_attempts = 0
        log_action(user.id, 'password_reset_otp', 'user', user.id, 'Password reset via email OTP')
        db.session.commit()
        flash('Your password has been reset successfully. You can now sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)
