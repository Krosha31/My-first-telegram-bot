from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove


TOKEN = '1659806911:AAE_ednsbLxGRhuFO8l00YghmBgfuXn0MQE'
reply_keyboard = [['/adress', '/phone'],
                      ['/site', '/work_time'], ['/set 5', '...']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


def echo(update, context):



def start(update, context):
    update.message.reply_text(
        "Привет! Я эхо-бот. Напишите мне что-нибудь, и я пришлю это назад!", reply_markup=markup)


def help(update, context):
    update.message.reply_text(
    "Я пока не умею помогать... Я только ваше эхо.")


def address(update, context):
    update.message.reply_text(
        "Адрес: г. Москва, ул. Льва Толстого, 16")


def phone(update, context):
    update.message.reply_text("Телефон: +7(495)776-3030")


def site(update, context):
    update.message.reply_text(
        "Сайт: http://www.yandex.ru/company")

def work_time(update, context):
    update.message.reply_text('6:00-22:00')


def close_keyboard(update, context):
    update.message.reply_text(
    "Ok",
    reply_markup=ReplyKeyboardRemove()
    )



def task(context):
    job = context.job
    context.bot.send_message(job.context[0], text=job.context[1])


def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.message.chat_id
    try:
        #args[0] должен содержать значение аргумента (секунды таймера)
        due = int(context.args[0])
        message = context.args[1]
        if due < 0:
            update.message.reply_text(
                'Извините, не умеем возвращаться в прошлое')
            return
        # Добавляем задачу в очередь
        # и останавливаем предыдущую (если она была)
        new_job = context.job_queue.run_once(task, due, context=[chat_id, message])
        # Запоминаем созданную задачу в данных чата.
        context.chat_data['job'] = new_job
        # Присылаем сообщение о том, что всё получилось.
        update.message.reply_text(f'Напомню через {due} секунд')
    except (IndexError, ValueError):
        update.message.reply_text('Использование: /set <секунд>')



def unset_timer(update, context):
    # Проверяем, что задача ставилась
    if 'job' not in context.chat_data:
        update.message.reply_text('Нет активного таймера')
        return
    job = context.chat_data['job']
    # планируем удаление задачи (выполнится, когда будет возможность)
    job.schedule_removal()
    # и очищаем пользовательские данные
    del context.chat_data['job']
    update.message.reply_text('Хорошо, вернулся сейчас!')



def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    text_handler = MessageHandler(Filters.text, echo)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("address", address))
    dp.add_handler(CommandHandler("phone", phone))
    dp.add_handler(CommandHandler("site", site))
    dp.add_handler(CommandHandler("work_time", work_time))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset_timer,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(text_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()



