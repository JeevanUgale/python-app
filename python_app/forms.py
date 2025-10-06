from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class UserForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired(), Length(max=120)])
    last_name = StringField('Last name', validators=[DataRequired(), Length(max=120)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=150)])
    qualification = StringField('Qualification', validators=[Length(max=200)])
    address = TextAreaField('Address', validators=[Length(max=1000)])
    submit = SubmitField('Save')
