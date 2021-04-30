from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, StringField, TextAreaField, SubmitField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    search_string = StringField("Поиск")
    submit = SubmitField('Найти')


class PriceForm(FlaskForm):
    min_price = IntegerField("Минимальная цена")
    max_price = IntegerField("Максимальная цена")
    submit1 = SubmitField("Найти")
