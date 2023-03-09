from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length


class TaskForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(3)])
    date = DateField("Date", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired(), Length(1)])
    submit = SubmitField("Submit")
