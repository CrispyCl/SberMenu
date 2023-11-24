from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class CategoryForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    main_category = SelectField("", choices=())
    image = FileField()
    submit = SubmitField("Добавить")
