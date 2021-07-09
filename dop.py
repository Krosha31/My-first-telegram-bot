from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove


TOKEN = '1659806911:AAE_ednsbLxGRhuFO8l00YghmBgfuXn0MQE'
reply_keyboard = [['/ass', '/phone'],
                      ['/site', '/work_time'], ['/set 5', '...']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)