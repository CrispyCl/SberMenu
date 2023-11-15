from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class LunchForm(FlaskForm):
    price = IntegerField("Цена")
    date = DateField("Дата")
    submit = SubmitField("Добавить")
