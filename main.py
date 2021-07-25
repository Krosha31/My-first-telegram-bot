from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from database import *
import processing_of_users_text as process
from random import choice
import traceback
from datetime import datetime, timedelta



TOKEN = '1659806911:AAE_ednsbLxGRhuFO8l00YghmBgfuXn0MQE'
reply_keyboard = [['/adress', '/phone'],
                      ['/site', '/work_time'], ['/set 5', '...']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
notify_answers = ['Будет сделано', 'Постараюсь не забыть', 'Обязательно напомню, если не забуду',
                 'Буду считать каждую секунду до этого события']
timer_answers = ['Уже ставлю', 'Как пожелаете', 'Поставил! Теперь вы точно не пропустите что-то важное']
nearest = datetime.now()


def processing_date(date_in):
    date_out = datetime.now()
    date_out += timedelta()
    return date_out


def format_time(n):
    n = str(n)
    if len(n) == 1:
        return '0' + n
    return n


def echo(update, context):
    text = update.message.text.split()
    dop = [i.lower() for i in text]
    try:
        type, other = process.processing_of_users_text(dop)
        if type == 't':
            dop = other[0]
            seconds = dop['h'] * 3600 + dop['m'] * 60 + dop['s']
            context.args = [seconds]
            set_timer(update, context)
        if type == 's':
            show_notifications(update, context)
        if type == 'n':
            other[0] = other[0]['D'] * 3600 * 24 + other[0]['h'] * 3600 + other[0]['m'] * 60 + other[0]['s']
            razn = session.query(User).filter_by(chat_id=update.message.chat_id)[0]
            other.append(datetime.now() + timedelta(seconds=other[0]))
            if razn.timezone >= 0:
                other[2] += timedelta(hours=razn.timezone)
            else:
                other[2] -= timedelta(hours=abs(razn.timezone))
            context.args = other[:]
            set_notification(update, context)
        if type == 'd':
            show_notifications(update, context)
            return 1

    except Exception:
        traceback.print_exc()
        update.message.reply_text('Я понял, что вы хотите, но, кажется, вы где-то допустили ошибку:('
                                  '\n Чтобы вспомнить, как пишутся команды, напишите /help')


def start(update, context):
    try:
        q = session.query(User).filter_by(chat_id=update.message.chat_id)[0]
    except:
        session.add(User(chat_id=update.message.chat.id, timezone=0, fill=False))
        session.commit()
    update.message.reply_text(
        "Привет! Меня зовут Bean, приятно познакомиться. Ты, видимо, первый раз здесь. Знаешь, я много чего умею "
        "Например, я могу напомнить тебе о чем нибудь. Если хочешь узнать весь список команд, напиши /commands",
        reply_markup=markup)
    update.message.reply_text("Для того, чтобы напоминания работали корректно, мне нужно знать твой часовой пояс. "
                              "Напиши, пожалуйста, на сколько часов время в твоем регионе отличается от московского "
                              "в формате +-0")
    return 1



def add_timezone(update, context):
    try:
        int(update.message.text)
        user = session.query(User).filter_by(chat_id=update.message.chat_id)[0]
        session.delete(user)
        session.add(User(chat_id=update.message.chat_id, timezone=int(update.message.text), fill=True))
        session.commit()
        update.message.reply_text("Отлично! Теперь напоминания будут работать корректно")
        return ConversationHandler.END
    except:
        traceback.print_exc()
        update.message.reply_text("Что-то пошло не так. Попробуйте ввести время снова")
        return 1


def stop(update, context):
    pass


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
    context.bot.sendMessage(chat_id=1825519862, text='qq')
    update.message.reply_text('6:00-22:00')


def close_keyboard(update, context):
    update.message.reply_text(
    "Ok",
    reply_markup=ReplyKeyboardRemove()
    )


def timer(context):
    job = context.job
    context.bot.send_message(job.context, text=f'Тик-так тик-так')


def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.message.chat_id
    #args[0] должен содержать значение аргумента (секунды таймера)
    due = context.args[0]
    if due < 0:
        update.message.reply_text(
            'Извините, не умею возвращаться в прошлое')
        return
    # Добавляем задачу в очередь
    # и останавливаем предыдущую (если она была)
    update.message.reply_text(choice(timer_answers))
    new_job = context.job_queue.run_once(timer, due, context=chat_id)


def notify(context):
    job = context.job
    context.bot.send_message(job.context[0], text=f'Вы просили меня напомнить вам: {job.context[1]}')


def set_notification(update, context):
    chat_id = update.message.chat_id
    due = context.args[0]
    if due < 0:
        update.message.reply_text(
            'Извините, не умею возвращаться в прошлое')
        return
    update.message.reply_text(choice(notify_answers))
    new_job = context.job_queue.run_once(notify, due, context=[chat_id, context.args[1]])
    try:
        context.chat_data['notify'].append([new_job, context.args[1], context.args[2]])
    except:
        context.chat_data['notify'] = [[new_job, context.args[1], context.args[2]]]


def show_notifications(update, context):
    if 'notify' not in context.chat_data or context.chat_data['notify'] == []:
        update.message.reply_text('Мне нечего вам напоминать')
    else:
        k = 1
        out = []
        now = datetime.now()
        context.chat_data['notify'] = sorted(context.chat_data['notify'], key=lambda x: x[2])
        d = []
        for i in context.chat_data['notify']:
            if now > i[2]:
                d.append(k - 1)
                continue
            dop = i[2] - now
            if dop.days < 1 and i[2].day - now.day == 1:
                time = f'завтра, в {format_time(i[2].hour)}:{format_time(i[2].minute)}:{format_time(i[2].second)}'
            elif 1 <= dop.days < 2 and i[2].day - now.day == 2:
                time = f'послезавтра, в {format_time(i[2].hour)}:{format_time(i[2].minute)}:{format_time(i[2].second)}'
            elif dop.days < 1 and i[2].day == now.day:
                time = f'сегодня, в {format_time(i[2].hour)}:{format_time(i[2].minute)}:{format_time(i[2].second)}'
            else:
                time = f'{format_time(i[2].day)}.{format_time(i[2].month)}.{i[2].year} в {format_time(i[2].hour)}:' \
                       f'{format_time(i[2].minute)}:{format_time(i[2].second)}'
            out += [f'{k}. Текст напоминания: {i[1]}\n    Время: {time}']
            out += '\n'
            k += 1
        for i in d:
            del context.chat_data['notify'][i]
        out = '\n'.join(out)
        if 'удалить' in update.message.text.lower():
            update.message.reply_text(f'Выбери напоминание для удаления(напиши его номер):\n\n{out} '
                                      f'Если ты хочешь удалить все напоминания - напиши "Все"\n'
                                      f'Чтобы выйти напиши "/stop"')
        else:
            update.message.reply_text(f'Вот, что я должен вам напомнить:\n\n{out}')


def delete_notification(update, context):
    try:
        if set(update.message.text) & set('1234567890'):
            number = int(update.message.text) - 1
            job = context.chat_data['notify'][number][0]
            job.schedule_removal()
            del context.chat_data['notify'][number]
            update.message.reply_text("Сделано")
        elif update.message.text.lower() == 'все':
            for i in context.chat_data["notify"]:
                i[0].schedule_removal()
            del context.chat_data["notify"]
            update.message.reply_text("Сделано")
        else:
            k = 1 / 0
        return ConversationHandler.END
    except:
        traceback.print_exc()
        update.message.reply_text("Кажется, где-то произошла ошибка. Попробуй еще раз или напиши /stop")


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    text_handler = MessageHandler(Filters.text, echo)

    dp.add_handler(ConversationHandler(entry_points=[CommandHandler("start", start)],
                   states={
                       # Функция читает ответ на первый вопрос и задаёт второй.
                       1: [MessageHandler(Filters.text, add_timezone)],
                   },
                    fallbacks=[CommandHandler('stop', stop)]

                    ))
    dp.add_handler(ConversationHandler(entry_points=[MessageHandler(Filters.text, echo)],
                                       states={
                                           # Функция читает ответ на первый вопрос и задаёт второй.
                                           1: [MessageHandler(Filters.text, delete_notification, pass_chat_data=True)]
                                       },
                                       fallbacks=[CommandHandler('stop', stop)]

                                       ))

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("address", address))
    dp.add_handler(CommandHandler("phone", phone))
    dp.add_handler(CommandHandler("site", site))
    dp.add_handler(CommandHandler("work_time", work_time))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(text_handler)
    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()



