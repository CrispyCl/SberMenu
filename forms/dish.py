from flask_wtf import FlaskForm
from wtforms import FileField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class DishForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание")
    price = IntegerField("Цена", validators=[DataRequired()])
    main_category = SelectField("", choices=())
    mass = IntegerField("Масса порции (г.)", default=100)
    image = FileField()
    submit = SubmitField("Добавить")
