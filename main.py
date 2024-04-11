import os
from os import abort
from flask import Flask, render_template, redirect, request, make_response, session, send_from_directory, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.user import RegisterForm, LoginForm
from data.users import User
from data import db_session


import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'static/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def index():
    date = datetime.date.today()
    temp = [[1,2,3] for j in range(3)]
    news = ["Здесь совсем скоро должен быть сайт", f"Сдача проекта уже через {26 - int(datetime.datetime.today().day)} дней", "Возможно я не укладываюсь, надо увеличивать темпы"]
    return render_template("index.html", title="Главная", address=[{"adress": "Татарская, 69", "id": "8762"}], date=date,
                        dates=[i for i in range(24)], data=[1,2,5,6,4,3,7,8,9,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2], news=news, temp=temp,)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

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

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/today")
def render_graphics():
    date = f"Расходы за {datetime.date.today()}"
    return render_template("render_graphics.html", date=date,
                           dates=[i for i in range(24)],
                           data=[1,2,5,6,4,3,7,8,9,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2])

def main():
    db_session.global_init("db/data.db")
    app.run(host='127.0.0.1', port=7070)


if __name__ == '__main__':
    main()
    db_sess = db_session.create_session()