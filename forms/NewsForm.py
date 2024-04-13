from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Клиент №{n}', validators=[DataRequired()])
    content = TextAreaField("Время")
    v0 = TextAreaField("Запрашиваемый обьем")
    v = TextAreaField("Выданный обьем")
