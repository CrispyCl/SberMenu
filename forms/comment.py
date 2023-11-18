from flask_wtf import FlaskForm
from wtforms import FileField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    comment = TextAreaField("Комментарий")
    submit = SubmitField("Добавить")
