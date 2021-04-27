from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, StringField, TextAreaField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class EditForm(FlaskForm):
    password = PasswordField('Изменить пароль')
    password_again = PasswordField('Повторите пароль')
    name = StringField('Изменить имя пользователя')
    about = TextAreaField("Изменить о себе")
    submit = SubmitField('Подтвердить')
