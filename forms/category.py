from flask_wtf import FlaskForm
from wtforms import FileField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CategoryForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    image = FileField()
    submit = SubmitField("Добавить")
