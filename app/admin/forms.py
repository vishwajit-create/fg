from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional


class UserCreateForm(FlaskForm):
    username = StringField('Username *', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email *', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password *', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password *',
                                     validators=[DataRequired(), EqualTo('password')])
    role_id = SelectField('Role *', coerce=int, validators=[DataRequired()])
    faculty_id = SelectField('Linked Faculty Profile', coerce=int, validators=[Optional()])
    submit = SubmitField('Create User')


class UserEditForm(FlaskForm):
    role_id = SelectField('Role *', coerce=int, validators=[DataRequired()])
    active = BooleanField('Account Active')
    submit = SubmitField('Save Changes')
