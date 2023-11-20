from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField


class CommentForm(FlaskForm):
    comment = TextAreaField("Комментарий")
    submit = SubmitField("Добавить")
