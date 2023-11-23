from flask_wtf import FlaskForm
from wtforms import FileField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CriteriaForm(FlaskForm):
    title = StringField("Критерий")
    submit = SubmitField("Добавить")