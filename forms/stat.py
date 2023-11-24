from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, DateField
from wtforms.validators import DataRequired
import datetime


class StatForm(FlaskForm):
    dish = SelectField("Блюдо", choices=[])
    date = DateField("Дата")
    submit = SubmitField("Вывести")
