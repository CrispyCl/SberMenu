from flask_wtf import FlaskForm
from wtforms import FileField, IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired


class DishForm(FlaskForm):
    name = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание")
    price = IntegerField("Цена", validators=[DataRequired()])
    picture = FileField()
