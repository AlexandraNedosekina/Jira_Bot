from logging import exception
import telebot
from datetime import date
from jirbl import *
from telebot import types
from configSasha import *

bot = telebot.TeleBot(tokenTg)

class Issue:
    summary = ""
    description = ""
    typeissue = ""
    assignee = ""
    priority = ""
    date = ""
    filesCount = 0
    dateList = list()
    edit = False

 #   , 'audio', 'document', 'photo', 'video', 'voice', 'contact'

@bot.message_handler(content_types=['text', 'audio', 'document', 'photo', 'video', 'voice', 'contact'])
def start(message):
    Issue.edit = False
    bot.register_next_step_handler(message, set_description)
    #Issue.description += message.text
    bot.send_message(message.chat.id,'Записываю' + message.content_type[0],reply_markup= keyboard_description())

def set_description(message):
    if message.text == 'Поставить задачу':
        bot.register_next_step_handler(message, set_summary_and_typeissue)
        bot.send_message(message.chat.id,'Введите тему задачи')
    elif message.text == 'Отменить постановку задачи':
        pass#дописать 
    else:
        bot.register_next_step_handler(message, set_description)
        Issue.description += "\n" + message.text
        #bot.edit_message_reply_markup(message.chat.id, reply_markup= keyboard_description())

def set_summary_and_typeissue(message):
    Issue.summary = message.text
    keyboard = types.InlineKeyboardMarkup()
    callback_button1 = types.InlineKeyboardButton(text="Задача", callback_data="task")
    callback_button2 = types.InlineKeyboardButton(text="Ошибка", callback_data="Bug")
    keyboard.add(callback_button1, callback_button2)
    bot.send_message(message.chat.id,'Выберите тип задачи:', reply_markup= keyboard)
#начало
def set_assignee(ID):
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="На меня", callback_data="assignee")
    keyboard.add(callback_button)
    bot.send_message(ID,'Введите Исполнителя.',reply_markup= keyboard)
    # Выбор исполнителя по имени , если имя есть в get_user_id , то ок
    # если нет, то ошибка exception
    if ID in get_user_id():
        return displayName
    else:
        print('Введите имя исполнителя')


    
    
#конец
def set_priority(ID):
    keyboard = types.InlineKeyboardMarkup()
    callback_lowest = types.InlineKeyboardButton(text="Lowest", callback_data="Lowest")
    callback_low = types.InlineKeyboardButton(text="Low", callback_data="Low")
    callback_medium = types.InlineKeyboardButton(text="Medium", callback_data="Medium")
    callback_high = types.InlineKeyboardButton(text="High", callback_data="High")
    callback_highest = types.InlineKeyboardButton(text="Highest", callback_data="Highest")
    keyboard.add(callback_lowest,callback_low,callback_medium,callback_high,callback_highest)
    bot.send_message(ID,'Выберите приоритет: ',reply_markup= keyboard)

def set_date(ID, message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Пропустить", callback_data="Skip")
    keyboard.add(callback_button)
    bot.register_next_step_handler(message, add_date)
    bot.send_message(ID,'Введите дату выполнения в формате ДД.ММ.ГГГГ',reply_markup= keyboard)

def add_date(message):
    try:
        date_message= message.text.split(".")
        date(int(date_message[2]), int(date_message[1]), int(date_message[0]))
    except:
        if not Issue.edit:
            set_date(message.chat.id, message)
            bot.edit_message_reply_markup(message.chat.id, message_id = message.message_id-1, reply_markup= None)
    else:
        Issue.date = message.text
        Issue.dateList = date_message
        bot.edit_message_reply_markup(message.chat.id, message_id = message.message_id-1, reply_markup= None)
        add_issue(message)

def add_issue(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button1 = types.InlineKeyboardButton(text="Да, отправить задачу в Jira", callback_data="Send")
    callback_button2 = types.InlineKeyboardButton(text="Нет, выбрать редактируемые поля", callback_data="Edit")
    keyboard.add(callback_button1, callback_button2)
    bot.send_message(message.chat.id, "1.Тема: " + Issue.summary +
                                    "\n2.Описание: " + Issue.description + "\nКоличество прикреплённых файлов: " + str(Issue.filesCount) +
                                    "\n3.Тип: " + Issue.typeissue +
                                    "\n4.Исполнитель: " + Issue.assignee +
                                    "\n5.Приоритет: " + Issue.priority +
                                    "\n6.Срок выполнения: " + Issue.date)
    bot.send_message(message.chat.id,"Данные введены верно?", reply_markup= keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == "task":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы выбрали тип Задача.")
            Issue.typeissue = "Задача"
            set_assignee(call.message.chat.id)
        elif call.data == "Bug":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы выбрали тип Ошибка.")
            Issue.typeissue = "Ошибка"
            set_assignee(call.message.chat.id)
        elif call.data == "assignee":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Исполнитель: " + search_user(str(call.from_user.id))[0])
            Issue.assignee = search_user(str(call.from_user.id))[0]
            set_priority(call.message.chat.id)
        elif call.data == "Lowest" or call.data == "Low" or call.data == "Medium" or call.data == "High" or call.data == "Highest":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Приоритет: " + call.data)
            Issue.priority = call.data
            set_date(call.message.chat.id, call.message)
        elif call.data == "Skip":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Без даты")
            Issue.date = "не указано"
            add_issue(call.message)
        elif call.data == "Send":
            bot.edit_message_text(chat_id= call.message.chat.id, message_id=call.message.message_id, text="Задача отправлена в Jira")
            create_issue(Issue.summary, Issue.description, Issue.typeissue, Issue.priority, Issue.dateList, Issue.assignee)
            bot.send_message(call.message.chat.id, "Задача поставлена в Jira")
            Issue.description = ""
            Issue.filesCount = 0
            Issue.dateList = list()
            Issue.edit = True
        # elif call.data == "Edit":
            # bot.edit_message_text(chat_id= call.message.chat.id, message_id=call.message.message_id, text="Введите номер редактируемого элемента")
            # Issue.edit = True
            # bot.register_next_step_handler(call.message, edit_issue)


def keyboard_description():
    markup_reply = telebot.types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    item_add_issue = telebot.types.KeyboardButton(text = 'Поставить задачу')#, callback_data = 'add issue')
    item_cancel_issue = telebot.types.KeyboardButton(text = 'Отменить постановку задачи')#, callback_data = 'cancel issue')

    markup_reply.add(item_add_issue,item_cancel_issue)
    return markup_reply

bot.polling(non_stop= True)
