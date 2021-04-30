from flask import Flask, render_template, make_response, jsonify, request
from werkzeug.utils import redirect
from data import db_session
from data.news import News, NewsForm
from data.users import User
import datetime
from forms.search import SearchForm, PriceForm
from forms.edit import EditForm
from forms.user import RegisterForm
from forms.loginform import LoginForm
from flask_restful import abort, Api
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
counter = False


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    form = SearchForm()
    price = PriceForm()
    db_sess = db_session.create_session()
    news = db_sess.query(News)
    if form.submit.data and form.validate():
        print("dad")
        db_sess = db_session.create_session()
        tag = form.search_string.data
        search = "%{}%".format(tag)
        news = db_sess.query(News).filter(News.title.like(search))
    if price.submit1.data and price.validate():
        if price.min_price.data > price.max_price.data:
            return render_template("index.html", message="Минимальная цена не может быть больше максимальной",
                                   news=news, counter="Удалить", form=form, price=price)
        else:
            db_sess = db_session.create_session()
            news = db_sess.query(News).filter(News.price > price.min_price.data, News.price < price.max_price.data)
    return render_template("index.html", news=news, counter="Удалить", form=form, price=price)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.price = form.price.data
        news.is_used = form.is_used.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news_view/<int:id>', methods=['GET'])
def news_view(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id)
    return render_template('news_view.html', title='Подробнее о записи', news=news)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        if current_user.getadmin():
            news = db_sess.query(News).filter(News.id == id).first()
        else:
            news = db_sess.query(News).filter(News.id == id,
                                              News.user == current_user
                                              ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.price.data = news.price
            form.is_used.data = news.is_used
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if current_user.getadmin():
            news = db_sess.query(News).filter(News.id == id).first()
        else:
            news = db_sess.query(News).filter(News.id == id,
                                              News.user == current_user
                                              ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.price = form.price.data
            news.is_used = form.is_used.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    if current_user.getadmin():
        news = db_sess.query(News).filter(News.id == id).first()
    else:
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    emails = ["gmail", "hotmail", "mail", "yandex", "yahoo"]
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if not any(email_service in form.email.data for email_service in emails):
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Invalid email")
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if len(form.password.data) < 8:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароль должен иметь не меньше 8 символов")
        if form.password.data.isdigit() or form.password.data.isalpha():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароль должен содержать буквы и цифры")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/user')
def user_page():
    db_sess = db_session.create_session()
    news = db_sess.query(News)
    return render_template('user.html', news=news)


@app.route('/liked', methods=['GET'])
def liked():
    # добавить get post???
    return render_template('liked.html', title="Избранное", )


@app.route('/liked_success/<int:id>', methods=['GET', 'POST'])
def liked_success(id):
    # добавить эту запись в избранное через базу данных
    # if (в базе данных есть айдишник этой записи, то вместо "Добавить в избранное, добавить удалить из избранного")
    return render_template('liked_success.html', title='Добавлено в избранное', liked_message="")


@app.route('/filter_new', methods=['GET', 'POST'])
def filter_new():
    global counter
    form = SearchForm()
    price = PriceForm()
    if counter is False:
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter((News.is_used == False))
        counter = True
        return render_template('index.html', news=news, counter="Добавить", form=form, price=price)
    else:
        counter = False
        return redirect("/")


@app.route('/user_edit', methods=['GET', 'POST'])
def user_edit():
    forma = EditForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id
                                          ).first()
        if user:
            forma.name.data = user.name
            forma.about.data = user.about
        else:
            abort(404)
    if forma.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id
                                          ).first()
        if user:
            if forma.password.data != forma.password_again.data:
                return render_template('user_edit.html', title='Регистрация',
                                       form=forma,
                                       message="Пароли не совпадают")

            if len(forma.password.data) < 8:
                return render_template('user_edit.html', title='Регистрация',
                                       form=forma,
                                       message="Пароль должен иметь не меньше 8 символов")
            if forma.password.data.isdigit() or forma.password.data.isalpha():
                return render_template('user_edit.html', title='Регистрация',
                                       form=forma,
                                       message="Пароль должен содержать буквы и цифры")
            user.set_password(forma.password.data)
            user.name = forma.name.data
            user.about = forma.about.data
            db_sess.commit()
            return redirect('/user')
        else:
            abort(404)
    return render_template('user_edit.html', title="Редактирование профиля", form=forma)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()
