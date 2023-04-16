from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length


images = set(['png', 'jpg', 'jpeg'])


class TaskForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(3)])
    date = DateField("Date", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired(), Length(1)])
    file = FileField("File", validators=[])
    submit = SubmitField("Submit")
