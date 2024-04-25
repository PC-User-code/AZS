import logging
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler
from data.config import BOT_TOKEN
import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

TIMER = 5  # таймер на 5 секунд

class Tg_bot():
    def remove_job_if_exists(name, context):
        """Удаляем задачу по имени.
        Возвращаем True если задача была успешно удалена."""
        current_jobs = context.job_queue.get_jobs_by_name(name)
        if not current_jobs:
            return False
        for job in current_jobs:
            job.schedule_removal()
        return True


    # Обычный обработчик, как и те, которыми мы пользовались раньше.
    async def set_timer(update, context):
        """Добавляем задачу в очередь"""
        chat_id = update.effective_message.chat_id
        # Добавляем задачу в очередь
        # и останавливаем предыдущую (если она была)
        job_removed = Tg_bot.self.remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(Tg_bot.task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)

        text = f'Вернусь через 5 с.!'
        if job_removed:
            text += ' Старая задача удалена.'
        await update.effective_message.reply_text(text)


    # Обычный обработчик, как и те, которыми мы пользовались раньше.
    async def set_timer_n(update, context):
        """Добавляем задачу в очередь"""
        TIMER = int(context.args[0])
        chat_id = update.effective_message.chat_id
        # Добавляем задачу в очередь
        # и останавливаем предыдущую (если она была)
        job_removed = Tg_bot.remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(Tg_bot.task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)
        text = f'Вернусь через {TIMER} с.!'
        if job_removed:
            text += ' Старая задача удалена.'
        await update.effective_message.reply_text(text)


    async def task(context):
        t = context.job.data
        """Выводит сообщение"""
        await context.bot.send_message(context.job.chat_id, text=f'КУКУ! {t}c. прошли!')


    async def unset(update, context):
        """Удаляет задачу, если пользователь передумал"""
        chat_id = update.message.chat_id
        job_removed = Tg_bot.remove_job_if_exists(str(chat_id), context)
        text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
        await update.message.reply_text(text)


    async def echo(update, context):
        await update.message.reply_text(f"Я получил сообщение {update.message.text}")


    async def start(update, context):
        user = update.effective_user
        await update.message.reply_html(
            rf"Привет {user.mention_html()}! Я эхо-бот. Напишите мне что-нибудь, и я пришлю это назад!",
        )


    async def help_command(update, context):
        await update.message.reply_text("Я пока не умею помогать... Я только ваше эхо.")


    async def time_command(update, context):
        h, m, s = datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second
        await update.message.reply_text(f"{h} часов {m} минут {s} секунд")


    async def date_command(update, context):
        await update.message.reply_text(
            f"{datetime.datetime.now().day}.{datetime.datetime.now().month}.{datetime.datetime.now().year}")


    def main():
        bot = Application.builder().token(BOT_TOKEN).build()
        text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, Tg_bot.echo)
        bot.add_handler(text_handler)
        bot.add_handler(CommandHandler("start", Tg_bot.start))
        bot.add_handler(CommandHandler("help", Tg_bot.help_command))
        bot.add_handler(CommandHandler("time", Tg_bot.time_command))
        bot.add_handler(CommandHandler("date", Tg_bot.date_command))
        bot.add_handler(CommandHandler("set", Tg_bot.set_timer))
        bot.add_handler(CommandHandler("unset", Tg_bot.unset))
        bot.add_handler(CommandHandler("set_timer", Tg_bot.set_timer_n))
        bot.run_polling()


if __name__ == "__main__":
    Tg_bot.main()