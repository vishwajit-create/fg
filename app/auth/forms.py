from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional


class LoginForm(FlaskForm):
    username = StringField('Username or Email',
                           validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class ProfileForm(FlaskForm):
    email = StringField('Email Address',
                        validators=[DataRequired(), Email(), Length(max=120)])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password',
                                 validators=[Optional(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[Optional(), EqualTo('new_password', message='Passwords must match.')],
    )
    submit = SubmitField('Save Security Settings')


class ForgotPasswordForm(FlaskForm):
    identifier = StringField('Username or Registered Email',
                             validators=[DataRequired(), Length(max=120)])
    submit = SubmitField('Send OTP')


class ResetPasswordOTPForm(FlaskForm):
    identifier = StringField('Username or Registered Email',
                             validators=[DataRequired(), Length(max=120)])
    otp = StringField('6-Digit OTP', validators=[DataRequired(), Length(min=6, max=6)])
    new_password = PasswordField('New Password',
                                 validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')],
    )
    submit = SubmitField('Reset Password')
