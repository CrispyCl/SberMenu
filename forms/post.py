from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()])
    text = TextAreaField("Текст")
    image = FileField()
    submit = SubmitField("Добавить")
