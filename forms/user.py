from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    email = EmailField("Почта", validators=[DataRequired()])
    name = StringField("Имя")
    surname = StringField("Фамилия")
    password = PasswordField("Пароль")
    password_again = PasswordField("Повторите пароль")
    submit = SubmitField("Войти")
