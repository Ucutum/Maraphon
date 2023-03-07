from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField
from wtforms.validators import DataRequired


class TaskForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Submit")
