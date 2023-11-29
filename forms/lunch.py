from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SubmitField


class LunchForm(FlaskForm):
    price = IntegerField("Цена")
    date = DateField("Дата")
    submit = SubmitField("Добавить")
