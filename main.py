from flask import Flask
from data import db_session
from data.users import User
from data.jobs import Jobs
from datetime import datetime

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
