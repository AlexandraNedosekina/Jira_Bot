import telebot
import jirbl
from telebot import types
import time
from config import *

bot = telebot.TeleBot("2086293075:AAGAy2mFCy3TemzxswZvY0bS_sFqkI8qF5A")

@bot.message_handler(content_types=['text', 'audio', 'document', 'photo', 'video', 'voice', 'contact'])
def start(message):
    bot.register_next_step_handler(message, set_description)
    #bot.edit_message_reply_markup(message.chat.id, reply_markup= keyboard_description())
    bot.send_message(message.chat.id,'Записываю',reply_markup= keyboard_description())

def set_description(message):
    if message.text == 'Поставить задачу':
        bot.register_next_step_handler(message, set_summary_and_typeissue)
        bot.send_message(message.chat.id,'Введите тему задачи')
    elif message.text == 'Отменить постановку задачи':
        pass
    else:
        bot.register_next_step_handler(message, set_description)
        #bot.edit_message_reply_markup(message.chat.id, reply_markup= keyboard_description())

def set_summary_and_typeissue(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button1 = types.InlineKeyboardButton(text="Задача", callback_data="task")
    callback_button2 = types.InlineKeyboardButton(text="Ошибка", callback_data="Bug")
    keyboard.add(callback_button1, callback_button2)
    bot.send_message(message.chat.id,'Выберите тип задачи:', reply_markup= keyboard)
    keyboard = types.InlineKeyboardMarkup()
    callback_button3 = types.InlineKeyboardButton(text="На меня", callback_data="assignee")
    keyboard.add(callback_button3)
    bot.send_message(message.chat.id,'Введите Исполнителя.',reply_markup= keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == "task":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы выбрали тип Задача.")
        elif call.data == "Bug":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы выбрали тип Ошибка.")
        elif call.data == "assignee":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Исполнитель: " + jirbl.search_user(str(call.from_user.id))[0])

def keyboard_description():
    markup_reply = telebot.types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    item_add_issue = telebot.types.KeyboardButton(text = 'Поставить задачу')#, callback_data = 'add issue')
    item_cancel_issue = telebot.types.KeyboardButton(text = 'Отменить постановку задачи')#, callback_data = 'cancel issue')

    markup_reply.add(item_add_issue,item_cancel_issue)
    return markup_reply

bot.polling(non_stop= True)
