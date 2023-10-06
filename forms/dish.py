from flask_wtf import FlaskForm
from wtforms import FileField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class DishForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание")
    price = IntegerField("Цена", validators=[DataRequired()])
    image = FileField()
    submit = SubmitField("Добавить")
