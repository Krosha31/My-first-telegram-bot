from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
import processing_of_users_text as process
from random import choice
import traceback



TOKEN = '1659806911:AAE_ednsbLxGRhuFO8l00YghmBgfuXn0MQE'
reply_keyboard = [['/adress', '/phone'],
                      ['/site', '/work_time'], ['/set 5', '...']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
notify_answers = ['Будет сделано', 'Постараюсь не забыть', 'Обязательно напомню, если не забуду',
                 'Буду считать каждую секунду до этого события']
timer_answers = ['Уже ставлю', 'Как пожелаете', 'Поставил! Теперь вы точно не пропустите что-то важное']

def echo(update, context):
    text = update.message.text.split()
    dop = [i.lower() for i in text]
    try:
        type, other = process.processing_of_users_text(dop)
        if type == 'n' or type == 't':
            context.args = other[:]
            context.args += [type]
            set_timer(update, context)
        if type == 's':
            show_notifications(update, context)
    except Exception:
        traceback.print_exc()
        update.message.reply_text('Я понял, что вы хотите, но, кажется, вы где-то допустили ошибку:('
                                  '\n Чтобы вспомнить, как пишутся команды, напишите /help')


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
    if job.context[2] == 'n':
        context.bot.send_message(job.context[0], text=f'Внимание! Вы просили напомнить вам {job.context[1]}')
        for i in range(1):
            pass

    elif job.context[2] == 't':
        context.bot.send_message(job.context[0], text=f'Тик-так тик-так {job.context[1]}')


def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.message.chat_id
    try:
        #args[0] должен содержать значение аргумента (секунды таймера)
        due, message, type = context.args
        if due < 0:
            update.message.reply_text(
                'Извините, не умею возвращаться в прошлое')
            return
        # Добавляем задачу в очередь
        # и останавливаем предыдущую (если она была)
        if type == 't':
            update.message.reply_text(choice(timer_answers))
        elif type == 'n':
            update.message.reply_text(choice(notify_answers))
        new_job = context.job_queue.run_once(task, due, context=[chat_id, message, type])
        # Запоминаем созданную задачу в данных чата.
        if 'job' not in context.chat_data and type == 'n':
            context.chat_data['job'] = [[new_job, message]]
        else:
            context.chat_data['job'].append([new_job, message])
    except (IndexError, ValueError):
        update.message.reply_text('Использование: /set <секунд>')



def unset_timer(update, context):
    if 'job' not in context.chat_data:
        update.message.reply_text('Нет активного таймера')
        return
    job = context.chat_data['job']
    # планируем удаление задачи (выполнится, когда будет возможность)
    job.schedule_removal()
    # и очищаем пользовательские данные
    del context.chat_data['job']
    update.message.reply_text('Хорошо, вернулся сейчас!')


def show_notifications(update, context):
    if 'job' not in context.chat_data or context.chat_data['job'] == []:
        update.message.reply_text('Мне нечего вам напоминать')
    else:
        k = 1
        out = []
        for i in context.chat_data['job']:
            out += [f'{k}. {i[1]}']
            k += 1
        out = '\n'.join(out)
        update.message.reply_text(f'Вот, что я должен вам напомнить:\n{out}')


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



