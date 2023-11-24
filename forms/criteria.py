from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class CriteriaForm(FlaskForm):
    title = StringField("Критерий")
    submit = SubmitField("Добавить")
