from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    email = EmailField("Почта", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    surname = StringField("Фамилия", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password_again = PasswordField("Повторите пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")
