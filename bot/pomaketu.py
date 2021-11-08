import telebot
import time
from config import *

bot = telebot.TeleBot(tokenTg)

@bot.message_handler(content_types=['text', 'audio', 'document', 'photo', 'video', 'voice', 'contact'])
def start(message):
    bot.register_next_step_handler(message, set_description)
    #bot.edit_message_reply_markup(message.chat.id, reply_markup= keyboard_description())
    bot.send_message(message.chat.id,'Записываю',reply_markup= keyboard_description())

def set_description(message):
    if message.text == 'Поставить задачу':
        pass
    elif message.text == 'Отменить постановку задачи':
        pass
    else:
        time.sleep(3)
        bot.register_next_step_handler(message, set_description)
        time.sleep(3)
        #bot.edit_message_reply_markup(message.chat.id, reply_markup= keyboard_description())

def keyboard_description():
    markup_reply = telebot.types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    item_add_issue = telebot.types.KeyboardButton(text = 'Поставить задачу')#, callback_data = 'add issue')
    item_cancel_issue = telebot.types.KeyboardButton(text = 'Отменить постановку задачи')#, callback_data = 'cancel issue')

    markup_reply.add(item_add_issue,item_cancel_issue)
    return markup_reply

bot.polling()
