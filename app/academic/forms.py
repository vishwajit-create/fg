from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class DepartmentForm(FlaskForm):
    code = StringField('Code *', validators=[DataRequired(), Length(max=20)])
    name = StringField('Name *', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Department')


class ProgramForm(FlaskForm):
    code = StringField('Code *', validators=[DataRequired(), Length(max=20)])
    name = StringField('Program Name *', validators=[DataRequired(), Length(max=150)])
    department_id = SelectField('Department *', coerce=int, validators=[DataRequired()])
    duration_years = IntegerField('Duration (Years)', default=3,
                                   validators=[NumberRange(min=1, max=10)])
    submit = SubmitField('Save Program')


class AcademicYearForm(FlaskForm):
    label = StringField('Label *', validators=[DataRequired(), Length(max=20)],
                        description='e.g. 2024-25')
    start_date = DateField('Start Date *', validators=[DataRequired()])
    end_date = DateField('End Date *', validators=[DataRequired()])
    active = BooleanField('Set as Current Year')
    submit = SubmitField('Save Academic Year')


class SectionForm(FlaskForm):
    program_id = SelectField('Program *', coerce=int, validators=[DataRequired()])
    academic_year_id = SelectField('Academic Year *', coerce=int, validators=[DataRequired()])
    semester = IntegerField('Semester *', validators=[DataRequired(), NumberRange(min=1, max=12)])
    section_name = StringField('Section Name *', validators=[DataRequired(), Length(max=20)],
                               description='e.g. A, B, C')
    submit = SubmitField('Save Section')


class SubjectForm(FlaskForm):
    code = StringField('Subject Code *', validators=[DataRequired(), Length(max=20)])
    title = StringField('Subject Title *', validators=[DataRequired(), Length(max=150)])
    program_id = SelectField('Program *', coerce=int, validators=[DataRequired()])
    semester = IntegerField('Semester', validators=[Optional(), NumberRange(min=1, max=12)])
    credits = IntegerField('Credits', default=3, validators=[NumberRange(min=0, max=10)])
    submit = SubmitField('Save Subject')
