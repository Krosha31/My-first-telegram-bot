from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from database import *
import processing_of_users_text as process
from Constans import *
from random import choice
import traceback
from datetime import datetime, timedelta
import requests
import pymorphy2
from pprint import pprint

base.metadata.create_all(engine)
reply_keyboard = [['/help', '/weather'],
                      ['/change_city', '/close']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

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
            context.args = other[:]
            set_notification(update, context)
        if type == 'd':
            dop = show_notifications(update, context)
            if dop is None:
                return 1
            else:
                return ConversationHandler.END
        if type == 'w':
            weather(update, context)

    except Exception:
        traceback.print_exc()
        update.message.reply_text('Что-то я совсем вас не понял. Попробуйте еще раз, может получится'
                                  '\n Чтобы вспомнить, как пишутся команды, напишите /help')


def start(update, context):
    try:
        q = session.query(User).filter_by(chat_id=update.message.chat_id)[0]
        update.message.reply_text("Второй раз команду /start писать не требуется)")
    except:
        session.add(User(chat_id=update.message.chat.id, timezone=0, city='', fill=False, lat=0, lon=0))
        session.commit()
        update.message.reply_text(
        "Привет! Меня зовут Bean, приятно познакомиться. Ты, видимо, первый раз здесь. Знаешь, я много чего умею "
        "Например, я могу напомнить тебе о чем нибудь. Если хочешь узнать весь список команд, напиши /commands")
        update.message.reply_text("Для того, чтобы напоминания и погода работали корректно, мне нужно знать твой часовой пояс. "
                              "Напиши, пожалуйста, название своего города, чтобы я мог найти его")
        context.chat_data['timezone'] = 'add'
        return 1


def change_timezone(update, context):
    update.message.reply_text("Напиши заново название своего города")
    context.chat_data['timezone'] = 'change'
    return 1


def add_timezone(update, context):
    try:
        url = 'https://geocode-maps.yandex.ru/1.x'
        city = requests.get(url=url, params={'apikey': GEO_KEY, 'geocode': update.message.text, 'format': 'json'}).json()
        name_city = city["response"]['GeoObjectCollection']['featureMember'][0]["GeoObject"]['metaDataProperty'][
            'GeocoderMetaData']['Address']['formatted'].split(', ')[1]
        coors = city["response"]['GeoObjectCollection']['featureMember'][0]["GeoObject"]['Point']['pos'].split()
        time = str(requests.get(url=f'http://api.geonames.org/timezone?lat={coors[1]}&lng={coors[0]}&username={TIMEZONE_KEY}&format=json').text).split()
        indi = False
        for i in time:
            if 'gmt' in i:
                for j in range(1, len(i)):
                    if i[j] == '>':
                        k1 = j + 1
                        indi = True
                    if indi and i[j] == '<':
                        k2 = j
                        break
                break
        dop = int(float(i[k1:k2]))
        timezone = dop - 3
        user = session.query(User).filter_by(chat_id=update.message.chat_id)[0]
        user.city = name_city
        user.timezone = timezone
        user.fill = True
        user.lat = coors[1]
        user.lon = coors[0]
        session.commit()
        if context.chat_data["timezone"] == 'add':
            update.message.reply_text("Отлично! Теперь напоминания и погода будут работать корректно")
            update.message.reply_text("Итак, давай же начинать", reply_markup=markup)
            help(update, context)
        else:
            update.message.reply_text("Ok")
        return ConversationHandler.END
    except:
        traceback.print_exc()
        update.message.reply_text("Что-то пошло не так. Попробуй ввести город снова")
        return 1


def stop(update, context):
    return ConversationHandler.END


def weather(update, context):
    user = session.query(User).filter_by(chat_id=update.message.chat_id)[0]
    lat = user.lat
    lon = user.lon
    weather = requests.get(url='https://api.weather.yandex.ru/v2/informers',
                       params={'lat': lat, 'lon': lon}, headers={'X-Yandex-API-Key': WEATHER_KEY}).json()
    morph = pymorphy2.MorphAnalyzer()
    words = user.city.split()
    new_city = []
    for word in words:
        dop = morph.parse(word)[0]
        dop = dop.inflect({'loct'})[0]
        new_city.append((dop.capitalize()))
    new_city = ' '.join(new_city)
    if '-' in user.city:
        new_city = new_city.split('-')
        for i in range(len(new_city)):
            new_city[i] = new_city[i].capitalize()
        new_city = '-'.join(new_city)
    update.message.reply_text(f'Сейчас в {new_city} {weather["fact"]["temp"]}°(ощущается как'
                              f' {weather["fact"]["feels_like"]}°), {condition[weather["fact"]["condition"]]}\n\nПодробнее: '
                              f'{weather["info"]["url"]}')



def help(update, context):
    f = open('help.txt', encoding='utf-8')
    update.message.reply_text(f.read())
    f.close()


def close_keyboard(update, context):
    update.message.reply_text(
    "Ok",
    reply_markup=ReplyKeyboardRemove()
    )

def open_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=markup
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
        if 'удали' in update.message.text.lower():
            return 'bad'
    else:
        k = 1
        out = []
        now = datetime.now()
        context.chat_data['notify'] = sorted(context.chat_data['notify'], key=lambda x: x[2])
        d = []
        timezone = session.query(User).filter_by(chat_id=update.message.chat_id).first().timezone
        for i in context.chat_data['notify']:
            if now > i[2]:
                d.append(k - 1)
                continue
            dop = i[2] - now
            i[2] += timedelta(hours=timezone)
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
        i[2] -= timedelta(hours=timezone)
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


def create_note_name(update, context):
    update.message.reply_text("Отлично, напиши мне название заметки")
    return 1


def create_note_description(update, context):
    update.message.reply_text("Теперь отправь мне саму заметку")
    context.chat_data['name'] = update.message.text
    return 2


def create_note(update, context):
    update.message.reply_text("Done! Заметка сохранена")

    note = Notes(user=update.message.chat_id, name=context.chat_data['name'], text=update.message.text)
    session.add(note)
    session.commit()
    return ConversationHandler.END

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
    dp.add_handler(ConversationHandler(entry_points=[CommandHandler("create_note", create_note_name)],
                                       states={
                                           # Функция читает ответ на первый вопрос и задаёт второй.
                                           1: [MessageHandler(Filters.text, create_note_description)],
                                           2: [MessageHandler(Filters.text, create_note)]
                                       },
                                       fallbacks=[CommandHandler('stop', stop)]

                                       ))
    dp.add_handler(ConversationHandler(entry_points=[CommandHandler("change_city", change_timezone)],
                                       states={
                                           # Функция читает ответ на первый вопрос и задаёт второй.
                                           1: [MessageHandler(Filters.text, add_timezone)],
                                       },
                                       fallbacks=[CommandHandler('stop', stop)]

                                       ))

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("weather", weather))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("open", open_keyboard))
    dp.add_handler(ConversationHandler(entry_points=[MessageHandler(Filters.text, echo, pass_chat_data=True)],
                                       states={
                                           # Функция читает ответ на первый вопрос и задаёт второй.
                                           1: [MessageHandler(Filters.text, delete_notification, pass_chat_data=True)]
                                       },
                                       fallbacks=[CommandHandler('stop', stop)]

                                       ))
    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()



