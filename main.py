import os
import csv
from flask import Flask, render_template, redirect, request, make_response, session, send_from_directory, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.user import RegisterForm, LoginForm
from data.server import Server
from data.users import User
from data import db_session
import datetime
import locale

locale.setlocale(locale.LC_TIME, 'ru')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
global base_data


def get_data(date):
    res = []
    if date == "today":
        res.append(".".join(str(datetime.datetime.today()).split()[0].split("-")[::-1]))
    else:
        month = datetime.datetime.strptime(str(datetime.datetime.today().month), '%m').strftime('%B').lower()
        if date == "week":
            week_start, week_end = datetime.date.today().day - datetime.datetime.today().weekday(), datetime.date.today().day - datetime.datetime.today().weekday() + 7
            res.append(f"{week_start} - {week_end} ({month})")
            res.append(week_start)
            res.append(week_end)
            res.append(datetime.datetime.today().month)
        else:
            res.append(month)
    return res


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'static/favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    price_l = 100
    db_sess = db_session.create_session()
    volume_day = sum([el.volume_res for el in db_sess.query(Server).filter(
        Server.date == ".".join(str(datetime.date.today()).split("-")[::-1])).all()])
    profit_day = volume_day * price_l
    temp = get_data("week")
    week = [str(el) + f".{'0' + str(temp[3]) if temp[3] < 10 else temp[3]}.{datetime.datetime.today().year}" for el in
            range(temp[1], temp[2] + 1)]
    volume_week = sum([int(el.volume_res) for el in db_sess.query(Server).filter(
        Server.date.in_(week)).all()])
    profit_week = volume_week * price_l
    volume_month = sum([el.volume_res for el in db_sess.query(Server).filter(
        Server.date.like(
            f"%.{'0' + str(temp[3]) if temp[3] < 10 else temp[3]}.{datetime.datetime.today().year}")).all()])
    profit_month = round(volume_month * price_l)
    temp = [["Статистика за сегодня", [f"Общий объем: {volume_day}", f"Прибыль: {profit_day}"], "/today"],
            ["Статистика за неделю", [f"Общий объем: {volume_week}", f"Прибыль: {profit_week}"], "/week"],
            ["Статистика за месяц", [f"Общий объем: {volume_month}", f"Прибыль: {profit_month}"], "/month"]]
    news = ["Здесь совсем скоро должен быть сайт",
            f"Сдача проекта уже через {26 - int(datetime.datetime.today().day)} дней",
            "Возможно я не укладываюсь, надо увеличивать темпы"]
    rows = [["Поддержка", "<a href='tg_bot'>Мы в телеграм</a>"],
            ["Увы, пока никто не сможет вам помочь"]]
    db_sess = db_session.create_session()
    table = db_sess.query(Server).filter(Server.date == "26.04.2024").all()
    data = [el.volume_res for el in table]
    dates = [round((float(el.time.split(":")[0]) + int(el.time.split(":")[1]) / 60), 2) for el in table]
    return render_template("index.html", title="Главная", base_data=base_data,
                           today=datetime.date.today(), dates=dates,
                           data=data, news=news,
                           temp=temp,
                           row1=rows[0], row2=rows[1])


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
    return render_template('login.html', title='Авторизация', form=form, base_data=base_data, )


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
                                   form=form, base_data=base_data,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, base_data=base_data,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, base_data=base_data)


@app.route("/today")
def day_statistic():
    statistic = get_data("today")
    db_sess = db_session.create_session()
    table = db_sess.query(Server).filter(Server.date == "26.04.2024").all()
    data = [el.volume_res for el in table]
    dates = [round((float(el.time.split(":")[0]) + int(el.time.split(":")[1]) / 60), 2) for el in table]
    return render_template("render_graphics.html", date=statistic[0], today=datetime.date.today(),
                           title="Статистика за день", base_data=base_data, not_today=False,
                           dates=dates, data=data, table_data=table)


@app.route("/week")
def week_statistic():
    statistic, start, end, month = get_data("week")
    print(statistic)
    db_sess = db_session.create_session()
    table0 = db_sess.query(Server).filter(Server.date.like(f"%.{'0' + str(month) if month < 10 else month}.2024")).all()
    sort_table = [el for el in table0 if
                  (start <= int(el.date.split(".")[0]) <= end) and (int(el.date.split(".")[1]) == month)]
    dates = sorted(list(set(sorted(list(set([el.date for el in sort_table]))))))
    data = [sum([el.volume_res for el in sort_table if el.date == date]) for date in dates]
    dates = [int(el.split(".")[0]) for el in dates]
    for i in range(len(dates)):
        print(dates[i], "->", data[i])
    return render_template("render_graphics.html", date=statistic, today=datetime.date.today(),
                           title="Статистика за неделю", not_today=True,
                           dates=dates, base_data=base_data, table_data=sort_table,
                           data=data)


@app.route("/month")
def month_statistic():
    db_sess = db_session.create_session()
    statistic = get_data("month")
    filter = f"%.{'0' + str(datetime.datetime.today().month) if int(datetime.datetime.today().month) < 10 else datetime.datetime.today().month}.{datetime.datetime.today().year}"
    table_data = db_sess.query(Server).filter(Server.date.like(filter)).all()
    dates = sorted(list(set([el.date for el in table_data])))
    data = [sum([int(el.volume_res) for el in table_data if el.date == date]) for date in dates]
    dates = [int(el.split(".")[0]) for el in dates]
    for i in range(len(dates)):
        print(dates[i], "->", data[i])
    return render_template("render_graphics.html", date=statistic[0], today=datetime.date.today(),
                           title="Статистика за месяц", not_today=True, table_data=table_data,
                           dates=dates, base_data=base_data, data=data)


@app.route("/tg_bot")
def tg_bot():
    return "Здесь будет Tg-бот"


@app.route('/upload', methods=['POST'])
def handle_file_upload():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file")
        if uploaded_files:
            f_name = ""
            for uploaded_file in uploaded_files:
                filename = uploaded_file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                f_name = filename
                uploaded_file.save(file_path)
            f = open(f"uploads/{f_name}", encoding="utf8")
            f = csv.DictReader(f, delimiter=';', quotechar='"')
            server = Server()
            for el in f:
                db_sess = db_session.create_session()
                server = Server()
                server.id_tranzaction = el["tranzaction"]
                server.id_column = el["id_colomn"]
                server.date = el["date"]
                server.time = el["time"]
                server.user_id = el["user_id"]
                server.volume_req = el["req_volume"]
                server.volume_res = el["res_volume"]
                db_sess.add(server)
                db_sess.commit()
            flash("Успешно")
        else:
            flash("Файл не выбран или не соответствует формату")
        return redirect("/today")


def main():
    db_session.global_init("db/data.db")
    app.run(host="127.0.0.1", port=7070, debug=True)


def test():
    db_session.global_init("db/data.db")
    db_sess = db_session.create_session()
    data = db_sess.query(Server).filter(
        Server.dt == "19.04.2024").all()  # .query().filter(Server.dt == "19.04.2024").all()
    for el in data:
        print(el.user_id)


if __name__ == '__main__':
    UPLOAD_FOLDER = '/temp'
    app.config['UPLOAD_FOLDER'] = 'uploads'
    base_data = {"address": "Татарская, 69",
                 "date": "-".join(str(datetime.datetime.today()).split()[0].split("-")[::-1])}
    main()
    db_sess = db_session.create_session()
