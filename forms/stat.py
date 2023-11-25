from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField


class StatForm(FlaskForm):
    dish = SelectField("Блюдо", choices=[])
    date = DateField("Дата")
    submit = SubmitField("Вывести")
