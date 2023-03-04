from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired


class SinginForm(FlaskForm):
    telegram = StringField("@telegram", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_again = PasswordField("Password again",
                                   validators=[DataRequired()])
    submit = SubmitField("SingIn")
