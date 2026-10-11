from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TelField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email


class FacultyForm(FlaskForm):
    employee_id = StringField('Employee ID *', validators=[DataRequired(), Length(max=30)])
    full_name = StringField('Full Name *', validators=[DataRequired(), Length(max=150)])
    department_id = SelectField('Department *', coerce=int, validators=[DataRequired()])
    designation = StringField('Designation', validators=[Optional(), Length(max=100)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    phone = TelField('Phone', validators=[Optional(), Length(max=20)])
    qualification = StringField('Qualification', validators=[Optional(), Length(max=150)])
    joining_date = DateField('Joining Date', validators=[Optional()])
    submit = SubmitField('Save Faculty')


class AssignmentForm(FlaskForm):
    faculty_id = SelectField('Faculty *', coerce=int, validators=[DataRequired()])
    section_id = SelectField('Section *', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Subject *', coerce=int, validators=[DataRequired()])
    academic_year_id = SelectField('Academic Year *', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign')
