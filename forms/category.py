from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField
from wtforms.validators import DataRequired


class CategoryForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    image = FileField()
    submit = SubmitField("Добавить")
