from flask import Flask, url_for, request, render_template, redirect, make_response, session, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from data import db_session, news_api
from data.users import User
from data.news import News
from data.category import Category
from forms.user import RegisterForm, LoginForm
from forms.news import NewsForm
from api import news_resources
from time import sleep
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    addy = input()
    db_session.global_init("db/" + addy)
    db_sess = db_session.create_session()
    user = db_sess.query(User).all()
    print(user)


if __name__ == '__main__':
    main()
