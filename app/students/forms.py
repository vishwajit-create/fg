from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TelField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email


class StudentForm(FlaskForm):
    roll_number = StringField('Roll Number *', validators=[DataRequired(), Length(max=30)])
    full_name = StringField('Full Name *', validators=[DataRequired(), Length(max=150)])
    program_id = SelectField('Program *', coerce=int, validators=[DataRequired()])
    section_id = SelectField('Section', coerce=int, validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    phone = TelField('Phone', validators=[Optional(), Length(max=20)])
    gender = SelectField('Gender', choices=[
        ('', '-- Select --'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')
    ], validators=[Optional()])
    admission_date = DateField('Admission Date *', validators=[DataRequired()])
    submit = SubmitField('Save Student')
