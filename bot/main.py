import telebot
from telebot import types
from config import tokenTg
from Jira_methods import *
from datetime import date
import os, glob

bot = telebot.TeleBot(tokenTg)

priorityDict = {
                '1' : 'Highest',
                '2' : 'High',
                '3' : 'Medium',
                '4' : 'Low',
                '5' : 'Lowest'
            }
usersDict = {}

class Data():
    description = ''
    email = ''
    password = ''
    accountId_DisplayName = []
    summary = ''
    issue_type = ''
    hint = {}
    assigneeID_assigneName = []
    priority = ''
    date = ''
    attachCount = 0
    attachName = {}

    issue_types = []
    edit = False

################################################################# РЕГИСТРАЦИЯ ###########################################################

@bot.message_handler(commands= 'start',content_types= 'text')
def start(message):
    usersDict[message.chat.id] = Data()
    bot.register_next_step_handler(message, get_email)
    bot.send_message(message.chat.id, "Введите вашу почту для регистрации.")
    
def get_email(message):
    usersDict[message.chat.id].email = message.text
    bot.register_next_step_handler(message, data_verification)
    bot.send_message(message.chat.id, "Укажите пароль.")

def data_verification(message):
    usersDict[message.chat.id].password = message.text
    try:
        usersDict[message.chat.id].accountId_DisplayName = authentication(usersDict[message.chat.id].email,
                                                                          usersDict[message.chat.id].password)
    except:
        bot.send_message(message.chat.id, "Данные введены не верно.")
        bot.send_message(message.chat.id, "Повторите попытку")
        start(message)
    else:
        try:
            os.makedirs("bot\\descriptions\\" + str(message.chat.id) + "_attacments")
        except:
            pass
        bot.send_message(message.chat.id, "Регистрация успешно завершена", reply_markup= keyboard_description())

############################################################### ХЕЛП #######################################################################

@bot.message_handler(commands= 'help',content_types= 'text')
def help(message):
    bot.send_message(message.chat.id, "/help - посмотреть хелп\n/start - изменить почту и пароль")

############################################### ЗАПОЛНЕНИЕ ОПИСАНИЯ И ДОБАВЛЕНИЕ ВЛОЖЕНИЙ #########################################################

@bot.message_handler(content_types=['document'])
def attach_document(message):
    #try:
        try:
            usersDict[message.chat.id].description += message.caption + ' '
        except:
            pass
        usersDict[message.chat.id].attachCount += 1
        i = str(usersDict[message.chat.id].attachCount)
        usersDict[message.chat.id].description += '(' + i + ')\n'
        name = message.document.file_name.split('.')
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'bot\descriptions\\' + str(message.chat.id) + '_attacments\\' + i + '.' + name[len(name) - 1]
        usersDict[message.chat.id].attachName[int(i)] = i + '.' + name[len(name) - 1]
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        
    #except:
    #x    start(message)
        
@bot.message_handler(content_types=['photo'])
def attach_photo(message):
    download_file(message, message.photo[len(message.photo)-1].file_id + '.jpg')

@bot.message_handler(content_types=['video'])
def attach_video(message):
    download_file(message, message.video.file_id + '.mp4')

@bot.message_handler(content_types=['audio'])
def attach_audio(message):
    download_file(message, message.audio.file_id + '.mp3')

@bot.message_handler(content_types=['text'])
def set_description(message):
    try:
        if usersDict[message.chat.id].edit:
            if message.text == '!Завершить редактирование описания':
                add_issue(message)
            elif message.text == '!Отменить постановку задачи':
                cancel(message,False)
            else:
                try:
                    usersDict[message.chat.id].description += message.text + '\n'# на случай если была отправлен какойто файлик вместо текста
                except:
                    pass
        else:
            if message.text == '!Поставить задачу':
                bot.register_next_step_handler(message, set_summary)
                bot.send_message(message.chat.id,'Введите тему задачи', reply_markup= keyboard_Cancel_issue())
            elif message.text == '!Отменить постановку задачи':
                cancel(message,False)
            else:
                usersDict[message.chat.id].description += message.text + '\n'
    except:
        start(message)

################################################### ЗАПОЛНЕНИЕ ЗАГОЛОВКА ###########################################################

def set_summary(message):
    if message.text == '!Отменить постановку задачи':
        cancel(message,False)
    elif message.content_type == 'text' and len(message.text) <= 255 and len(message.text.splitlines()) == 1:
        usersDict[message.chat.id].summary = message.text
        if usersDict[message.chat.id].edit:
            add_issue(message)
        else:
            set_issue_type(message)
    else:
        bot.register_next_step_handler(message, set_summary)
        bot.send_message(message.chat.id, 'Данные введены неверно.\nВведите тему в одну строку и не больше 255 символов!')

################################################## ЗАПОЛНЕНИЕ ТИПА ЗАДАЧИ ####################################################################

def set_issue_type(message):
    keyboard = types.InlineKeyboardMarkup()
    usersDict[message.chat.id].issue_types = get_issue_types(usersDict[message.chat.id].email,usersDict[message.chat.id].password)

    issuetypes = usersDict[message.chat.id].issue_types
    knops=[[]]
    for i in range(len(issuetypes) // 2):
        knops.append([types.InlineKeyboardButton(text=issuetypes[2*i], callback_data=issuetypes[2*i]),
                      types.InlineKeyboardButton(text=issuetypes[2*i + 1], callback_data=issuetypes[2*i + 1])])
    if len(issuetypes) % 2 == 1:
        knops.append([types.InlineKeyboardButton(text=issuetypes[len(issuetypes) - 1], callback_data=issuetypes[len(issuetypes) - 1])])
    keyboard = types.InlineKeyboardMarkup(knops)

    bot.register_next_step_handler(message, message_in_issue_type)
    bot.send_message(message.chat.id,'Выберите тип задачи:', reply_markup= keyboard)

def message_in_issue_type(message):
    if message.text == '!Отменить постановку задачи':
        cancel(message,False)
    else:
        bot.edit_message_reply_markup(message.chat.id, message_id= message.message_id-1, reply_markup= None)
        bot.send_message(message.chat.id, 'Нажмите на кнопку с нужным типом задачи')
        set_issue_type(message)
        

################################################### НАЗНАЧЕНИЕ ИСПОЛНИТЕЛЯ ########################################################

def set_assignee(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='На меня', callback_data='assignee'))
    bot.register_next_step_handler(message,get_assignee)
    bot.send_message(message.chat.id,'Введите Исполнителя.',reply_markup= keyboard)

def get_assignee(message):
    bot.edit_message_reply_markup(message.chat.id, message_id= message.message_id-1, reply_markup= None)
    if message.content_type == 'text':
        usersDict[message.chat.id].hint = get_assigneeID(usersDict[message.chat.id].email, usersDict[message.chat.id].password, message.text)
        if len(usersDict[message.chat.id].hint.keys()) > 1:
            keyboard = types.InlineKeyboardMarkup()
            keys = list(usersDict[message.chat.id].hint.keys())
            for i in range(len(keys)):
                keyboard.add(types.InlineKeyboardButton(text=keys[i], callback_data=keys[i]))
            bot.register_next_step_handler(message, get_assignee)
            bot.send_message(message.chat.id,'Выберите Исполнителя.',reply_markup= keyboard)
        elif len(usersDict[message.chat.id].hint.keys()) == 1:
            assigneeItems = list(list(usersDict[message.chat.id].hint.items())[0])
            usersDict[message.chat.id].assigneeID_assigneName = [assigneeItems[1], assigneeItems[0]]
            bot.send_message(message.chat.id, f'Исполнитель: {usersDict[message.chat.id].assigneeID_assigneName[1]}.')
            if usersDict[message.chat.id].edit:
                add_issue(message)
            else:
                set_priority(message)
        else:
            if message.text == '!Отменить постановку задачи':
                cancel(message,False)
            else:
                bot.send_message(message.chat.id, 'Такой пользователь не найден!')
                set_assignee(message)
    else:
        bot.send_message(message.chat.id, 'Неверный формат сообщения')
        set_assignee(message)
################################################## МЕТОД ДЛЯ УСТАНОВКИ ПРИОРИТЕТА ЗАДАЧИ #################################################

def set_priority(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Lowest", callback_data='5'),
                 types.InlineKeyboardButton(text="Low", callback_data='4'),
                 types.InlineKeyboardButton(text="Medium", callback_data='3'),
                 types.InlineKeyboardButton(text="High", callback_data='2'),
                 types.InlineKeyboardButton(text="Highest", callback_data='1'))
    bot.register_next_step_handler(message, message_in_priority)
    bot.send_message(message.chat.id,'Выберите приоритет: ',reply_markup= keyboard)

def message_in_priority(message):
    if message.text == '!Отменить постановку задачи':
        cancel(message,False)
    else:
        bot.edit_message_reply_markup(message.chat.id, message_id= message.message_id-1, reply_markup= None)
        bot.send_message(message.chat.id, 'Нажмите на кнопку с нужным приоритетом')
        set_priority(message)

###################################################### МЕТОД ДЛЯ УСТАНОВКИ ДАТЫ ##########################################################

def set_date(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Пропустить", callback_data="SkipDate"))
    bot.register_next_step_handler(message, add_date)
    bot.send_message(message.chat.id,'Введите дату выполнения в формате ДД.ММ:',reply_markup= keyboard)

def add_date(message):
    bot.edit_message_reply_markup(message.chat.id, message_id= message.message_id-1, reply_markup= None)
    if message.content_type == 'text':
        datemsg = message.text.split('.')
        if len(datemsg) != 2 or len(datemsg[0]) != 2 or len(datemsg[1]) != 2:
            datemsg = ['F']
        try:
            datemsg = list(map(int,datemsg))
            year = date.today().year
            if datemsg[1] < date.today().month or (datemsg[1] == date.today().month and datemsg[0]< date.today().day):
                year+=1
            date(year,datemsg[1],datemsg[0])
        except:
            if message.text == '!Отменить постановку задачи':
                cancel(message,False)
            else:
                bot.send_message(message.chat.id,'Дата введена некорректно')
                set_date(message)
        else:
            usersDict[message.chat.id].date = message.text + '.' + str(year)
            add_issue(message)
    else:
        bot.send_message(message.chat.id,'Дата введена некорректно')
        set_date(message)

####################################################### МЕТОД ДОБАВЛЕНИЯ ЗАДАЧИ В ДЖИРА ##########################################################################

def add_issue(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да, отправить задачу в Jira', callback_data='Send'),
                 types.InlineKeyboardButton(text='Нет, выбрать редактируемые поля', callback_data='Edit'))
    bot.register_next_step_handler(message, massage_in_issue)
    bot.send_message(message.chat.id, f'1.Тема: {usersDict[message.chat.id].summary}' +
                                    f'\n2.Описание: {usersDict[message.chat.id].description[:-1]}' +
                                    f'\n3.Тип: {usersDict[message.chat.id].issue_type}' +
                                    f'\n4.Исполнитель: {usersDict[message.chat.id].assigneeID_assigneName[1]}' +
                                    f'\n5.Приоритет: {priorityDict.get(usersDict[message.chat.id].priority)}' + 
                                    f'\n6.Срок выполнения: {usersDict[message.chat.id].date}' + 
                                    f'\nКоличество прикреплённых файлов: {str(usersDict[message.chat.id].attachCount)}',
                                    reply_markup= keyboard_Cancel_issue())
    bot.send_message(message.chat.id ,"Данные введены верно?", reply_markup= keyboard)

def massage_in_issue(message):
    if message.text == '!Отменить постановку задачи':
        cancel(message,False)
    else:
        bot.edit_message_reply_markup(message.chat.id, message_id= message.message_id-1, reply_markup= None)
        bot.send_message(message.chat.id, 'Пожалуйста, выберите из предложенного.')
        add_issue(message)

################################################### МЕТОД ДЛЯ ОБРАБОТКИ CALLBACK ДАННЫХ #########################################

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data in usersDict[call.message.chat.id].issue_types:
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id, 
                                  text=f'Вы выбрали тип {call.data}.')
            usersDict[call.message.chat.id].issue_type = call.data
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            if usersDict[call.message.chat.id].edit:
                add_issue(call.message)
            else:
                set_assignee(call.message)

        elif call.data == 'assignee':
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id, 
                                  text=f'Исполнитель: {usersDict[call.message.chat.id].accountId_DisplayName[1]}.')
            usersDict[call.message.chat.id].assigneeID_assigneName = usersDict[call.message.chat.id].accountId_DisplayName
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            if usersDict[call.message.chat.id].edit:
                add_issue(call.message)
            else:
                set_priority(call.message)

        elif call.data in usersDict[call.message.chat.id].hint.keys():
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id, 
                                  text=f'Исполнитель: {call.data}.')
            usersDict[call.message.chat.id].assigneeID_assigneName = [usersDict[call.message.chat.id].hint[call.data], call.data]
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            if usersDict[call.message.chat.id].edit:
                add_issue(call.message)
            else:
                set_priority(call.message)

        elif call.data.isnumeric():
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id, 
                                  text=f'Приоритет: {priorityDict.get(call.data)}.')
            usersDict[call.message.chat.id].priority = call.data
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            if usersDict[call.message.chat.id].edit:
                add_issue(call.message)
            else:
                set_date(call.message)

        elif call.data == 'SkipDate':
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id, 
                                  text='Без даты')
            usersDict[call.message.chat.id].date = 'Без даты'
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            add_issue(call.message)

        elif call.data == 'Send':
            bot.edit_message_text(chat_id= call.message.chat.id,
                                  message_id=call.message.message_id, 
                                  text="Задача отправлена в Jira")
            issue = create_issue(usersDict[call.message.chat.id].email, usersDict[call.message.chat.id].password,
                                 usersDict[call.message.chat.id].summary, usersDict[call.message.chat.id].description,
                                 usersDict[call.message.chat.id].issue_type, usersDict[call.message.chat.id].priority,
                                 usersDict[call.message.chat.id].date.split('.'), usersDict[call.message.chat.id].assigneeID_assigneName[0])
            send_attachments(call.message.chat.id,issue)
            cancel(call.message, True)
            bot.send_message(call.message.chat.id, "Задача поставлена в Jira",reply_markup= keyboard_description())

        elif call.data == 'Edit':
            bot.edit_message_text(chat_id= call.message.chat.id, 
                                  message_id=call.message.message_id, 
                                  text="Выберите редактируемый элемент")
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= keyboard_edit_element())
            usersDict[call.message.chat.id].edit = True

        elif call.data == 'EditSummary':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            bot.register_next_step_handler(call.message, set_summary)
            bot.send_message(call.message.chat.id,'Введите тему задачи')
        elif call.data == 'EditDescription':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            usersDict[call.message.chat.id].description = ''
            delete_files(call.message.chat.id)
            usersDict[call.message.chat.id].attachCount = 0
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            bot.send_message(call.message.chat.id,
                             'введите описание, после чего нажмите кнопку \n!Завершить редактирование описания',
                             reply_markup= keyboard_edit_description())
        elif call.data == 'EditTypeIssue':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            set_issue_type(call.message)
        elif call.data == 'EditAssignee':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            set_assignee(call.message)
        elif call.data == 'EditPriority':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            set_priority(call.message)
        elif call.data == 'EditDate':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            set_date(call.message)
        elif call.data == 'back':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            add_issue(call.message)
            
######################################################### ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ########################################################

def keyboard_Cancel_issue():
    markup_reply = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True,)
    markup_reply.add(types.KeyboardButton(text = '!Отменить постановку задачи'))
    return markup_reply

def keyboard_edit_element():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Тема', callback_data='EditSummary'),
                 types.InlineKeyboardButton(text='Описание', callback_data='EditDescription'),
                 types.InlineKeyboardButton(text='Тип', callback_data='EditTypeIssue'),
                 types.InlineKeyboardButton(text='Исполнитель', callback_data='EditAssignee'),
                 types.InlineKeyboardButton(text='Приоритет', callback_data='EditPriority'),
                 types.InlineKeyboardButton(text='Срок выполнения', callback_data='EditDate'))
    keyboard.add(types.InlineKeyboardButton(text='Обратно', callback_data='back'))
    return keyboard

def keyboard_edit_description():
    markup_reply = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    markup_reply.add(types.KeyboardButton(text = '!Отменить постановку задачи'),
                     types.KeyboardButton(text = '!Завершить редактирование описания'))
    return markup_reply

def keyboard_description():
    markup_reply = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    item_add_issue = types.KeyboardButton(text = '!Поставить задачу')
    item_cancel_issue = types.KeyboardButton(text = '!Отменить постановку задачи')

    markup_reply.add(item_cancel_issue, item_add_issue)
    return markup_reply

def delete_files(id):
    files = glob.glob('bot\\descriptions\\' + str(id) + '_attacments\\*')
    for f in files:
        os.remove(f)

def send_attachments(ID,issue):
    for key in range(usersDict[ID].attachCount, 0, -1):
        add_attachments(usersDict[ID].email, usersDict[ID].password, issue, usersDict[ID].attachName[key],
                        'bot\\descriptions\\' + str(ID) + '_attacments\\' + usersDict[ID].attachName[key])

def download_file(message,file):
    try:
        try:
            usersDict[message.chat.id].description += message.caption + ' '
        except:
            pass
        usersDict[message.chat.id].attachCount += 1
        i = str(usersDict[message.chat.id].attachCount)
        usersDict[message.chat.id].description += '(' + i + ')\n'
        file_info = bot.get_file(file.split('.')[0])
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'bot\descriptions\\' + str(message.chat.id) + '_attacments\\' + i + '.' + file.split('.')[1]
        usersDict[message.chat.id].attachName[int(i)] = i + '.' + file.split('.')[1]
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
    except:
        start(message)

def cancel(message,send):
    usersDict[message.chat.id].summary = ''
    usersDict[message.chat.id].description = ''
    delete_files(message.chat.id)
    usersDict[message.chat.id].issue_type = ''
    usersDict[message.chat.id].assigneeID_assigneName = []
    usersDict[message.chat.id].priority = ''
    usersDict[message.chat.id].date = ''
    usersDict[message.chat.id].edit = False
    usersDict[message.chat.id].attachCount = 0
    usersDict[message.chat.id].hint = {}
    usersDict[message.chat.id].attachName = {}
    try:
        bot.edit_message_reply_markup(message.chat.id, message_id= message.message_id-1, reply_markup= None)
    except:
        pass
    if not send:
        bot.send_message(message.chat.id, 'Задача отменена', reply_markup= keyboard_description())

bot.polling(none_stop=True)