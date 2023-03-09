from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class MaraphonSettingsForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(5)])
    submit = SubmitField("Submit")
