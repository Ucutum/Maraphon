from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length


class SinginForm(FlaskForm):
    telegram = StringField("@telegram", validators=[DataRequired(), Length(2)])
    name = StringField("Name", validators=[DataRequired(), Length(6)])
    password = PasswordField("Password", validators=[DataRequired(), Length(3)])
    password_again = PasswordField("Password again",
                                   validators=[DataRequired()])
    submit = SubmitField("SingIn")
