import csv
import logging
import os
import requests
from telegram.ext import Application, MessageHandler, filters
from data.config import BOT_TOKEN
from telegram.ext import CommandHandler
from data.server import Server
from data.users import User
from data import db_session
import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
TIMER = 5  # таймер на 5 секунд


# Функция cretae_report создает отчет за определенный период день/неделя/месяц
def create_report(date):
    db_sess = db_session.create_session()
    if date == "day":
        data = db_sess.query(Server).filter(Server.date == "26.04.2024").all()
    elif date == "week":
        start, end, month = datetime.date.today().day - datetime.datetime.today().weekday(), datetime.date.today().day - datetime.datetime.today().weekday() + 7, datetime.datetime.today().month
        table0 = db_sess.query(Server).filter(
            Server.date.like(f"%.{'0' + str(month) if month < 10 else month}.2024")).all()
        data = [el for el in table0 if
                (start <= int(el.date.split(".")[0]) <= end) and (int(el.date.split(".")[1]) == month)]
    else:
        filter = f"%.{'0' + str(datetime.datetime.today().month) if int(datetime.datetime.today().month) < 10 else datetime.datetime.today().month}.{datetime.datetime.today().year}"
        data = db_sess.query(Server).filter(Server.date.like(filter)).all()
    filename = ""
    os.chdir(f"temp/reports/{date}")
    last_name = [el for el in os.listdir()]
    if len(last_name) == 0:
        print("Файлов пока нет")
    else:
        print("last_name ->", last_name[-1])
    dt = '-'.join(str(datetime.datetime.today()).split()[0].split('-')[::-1])
    # получение имени последнего отчета создание имени для нового отчета
    if len(last_name) == 0:
        with open(f"report_{dt}.csv", 'wb') as f:
            writer = csv.writer(f)
        filename = f"report_{dt}.csv"
    elif dt == last_name[-1][:-4].split("_")[1]:
        n = 1 if len(last_name[-1].split("_")) == 2 else (int(last_name[-1][:-4].split("_")[2]) + 1)
        with open(f"report_{dt}_{n}.csv", 'wb') as f:
            writer = csv.writer(f)
        filename = f"report_{dt}_{n}.csv"
    print(filename)
    with open(filename, 'w', newline='') as f:
        fieldnames = ["date", "time", "tranzaction", "id_column", "user_id", "req_volume", "res_volume"]
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fieldnames)
        for el in data:
            print({"date": el.date, "time": el.time, "tranzaction": el.id_tranzaction,
                   "id_column": el.id_column, "user_id": el.user_id,
                   "req_volume": el.volume_req, "res_volume": el.volume_res})
            writer.writerow(
                [el.date, el.time, el.id_tranzaction, el.id_column, el.user_id, el.volume_req, el.volume_res])
    os.chdir("../../..")
    print("filename ->", filename)
    return filename


async def start(update, context):

    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я AZS_бот. Я пока умею только формировать отчет за день/неделю/месяц. Для получения справки отправьте /help",
    )


async def help_command(update, context):
    help_text = """Мои функции позволяют
    /get_data __ 
    Получить отчет за промежуток (день / неделя / месяц )
    Формат ввода -> arg - "day" / "week" / "month"     
    """
    await update.message.reply_text(help_text)


# Функция-редактор уровня доступа пользователя
async def edit_level(update, context):
    db_sess = db_session.create_session()
    msg = update.message.text.split()[1:3]
    if len(msg) == 2:
        print("Users", [el.name for el in db_sess.query(User).all()])
        print(f"name - {msg[0]}, level - {msg[1]}")
        if msg[0] in [el.name for el in db_sess.query(User).all()]:
            if 0 <= int(msg[1]) <= 2:
                username, level = msg
                user = db_sess.query(User).filter(User.name == username).first()
                user.access = level
                db_sess.commit()
                db_sess.commit()
                await update.message.reply_text("Успешно изменено")
            else:
                await update.message.reply_text("Введите корректное значения уровня доступа (0 - 2)")
        else:
            await update.message.reply_text(
                "Пользователь не найден. Проверьте, правильно ли написали имя, и попробуйте ещё раз")
    else:
        await update.message.reply("!Неверный формат ввода!    \n"
                                        " Следуйте макету -> /edit_level __username__ __new_level_success(0-2)__")


async def get_data(update, context):
    db_sess = db_session.create_session()
    date = update.message.text.split()[1]
    dates = {"day": "сегодня", "week": "неделю", "month": "месяц"}
    if date in ["day", "week", "month"]:
        url = 'https://api.telegram.org/bot{}/sendDocument'.format(BOT_TOKEN)
        n = 1
        data = {'chat_id': update.message.chat_id,
                'caption': f'Отчет №{n} от {".".join(str(datetime.datetime.today()).split()[0].split("-")[::-1])} за {dates[date]}'}
        filename = create_report(date)
        if filename:
            with open(f"temp/reports/{date}/{filename}", 'rb') as f:
                files = {'document': f}
                response = requests.post(url, data=data, files=files)
        else:
            await update.message.reply_text("Данных пока нет")
    else:
        await update.message.reply_text('Неверный формат ввода. Следуйте макету ->  arg - "day" / "week" / "month" ')


def main():
    db_session.global_init("db/data.db")
    db_sess = db_session.create_session()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("edit_level", edit_level))
    application.add_handler(CommandHandler("get_data", get_data))
    application.run_polling()


if __name__ == '__main__':
    main()
