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
    assigneeID_assigneName = []
    priority = ''
    date = ''

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

############################################### ЗАПОЛНЕНИЕ ОПИСАНИЯ И ДОБАВЛЕНИЕ ВЛОЖЕНИЙ #########################################################

@bot.message_handler(content_types=['document'])
def attach_document(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    src = 'bot\descriptions\\' + str(message.chat.id) + '_attacments\\' + message.document.file_name
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
        
@bot.message_handler(content_types=['photo'])
def attach_photo(message):
    download_file(message.chat.id, message.photo[len(message.photo)-1].file_id + '.jpg')

@bot.message_handler(content_types=['video'])
def attach_video(message):
    download_file(message.chat.id, message.video.file_id + '.mp4')

@bot.message_handler(content_types=['audio'])
def attach_audio(message):
    download_file(message.chat.id, message.audio.file_id + '.mp3')

@bot.message_handler(content_types=['text'])
def set_description(message):
    if usersDict[message.chat.id].edit:
        if message.text == '!Завершить редактирование описания':
            add_issue(message.chat.id)
        else:
            usersDict[message.chat.id].description += message.text + '\n'
    else:
        if message.text == '!Поставить задачу':
            bot.register_next_step_handler(message, set_summary)
            bot.send_message(message.chat.id,'Введите тему задачи', reply_markup= keyboard_Cancel_issue())
        elif message.text == '!Отменить постановку задачи':
            cancel(message,False)
        else:
            usersDict[message.chat.id].description += message.text + '\n'

################################################### ЗАПОЛНЕНИЕ ЗАГОЛОВКА ###########################################################

def set_summary(message):
    if message.text == '!Отменить постановку задачи':
        cancel(message,False)
    else:
        usersDict[message.chat.id].summary = message.text
        usersDict[message.chat.id].at_me = False
        if usersDict[message.chat.id].edit:
            add_issue(message.chat.id)
        else:
            set_issue_type(message.chat.id)

################################################## ЗАПОЛНЕНИЕ ТИПА ЗАДАЧИ ####################################################################

def set_issue_type(ID):
    keyboard = types.InlineKeyboardMarkup()
    usersDict[ID].issue_types = get_issue_types(usersDict[ID].email,usersDict[ID].password)

    issuetypes = usersDict[ID].issue_types
    knops=[[]]
    for i in range(len(issuetypes) // 2):
        knops.append([types.InlineKeyboardButton(text=issuetypes[2*i], callback_data=issuetypes[2*i]),
                      types.InlineKeyboardButton(text=issuetypes[2*i + 1], callback_data=issuetypes[2*i + 1])])
    if len(issuetypes) % 2 == 1:
        knops.append([types.InlineKeyboardButton(text=issuetypes[len(issuetypes) - 1], callback_data=issuetypes[len(issuetypes) - 1])])
    keyboard = types.InlineKeyboardMarkup(knops)
    
    bot.send_message(ID,'Выберите тип задачи:', reply_markup= keyboard)

################################################### НАЗНАЧЕНИЕ ИСПОЛНИТЕЛЯ ########################################################

def set_assignee(ID):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='меня', callback_data='assigneeMe'),
                 types.InlineKeyboardButton(text='Кого-то другого', callback_data='assignee'))
    bot.send_message(ID,'Кого назначить исполнителем?',reply_markup= keyboard)

def get_assignee(message):
    usersDict[message.chat.id].assigneeID_assigneName = get_assigneeID(usersDict[message.chat.id].email,
                                                                       usersDict[message.chat.id].password, message.text)
    if len(usersDict[message.chat.id].assigneeID_assigneName) > 0:
        bot.send_message(message.chat.id, 'Мы вас нашли!!!😎📸')
        if usersDict[message.chat.id].edit:
            add_issue(message.chat.id)
        else:
            set_priority(message.chat.id)
    else:
        if message.text == '!Отменить постановку задачи':
            cancel(message,False)
        else:
            bot.send_message(message.chat.id, 'Такой пользователь не найден😞')
            set_assignee(message.chat.id)

################################################## МЕТОД ДЛЯ УСТАНОВКИ ПРИОРИТЕТА ЗАДАЧИ #################################################

def set_priority(ID):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Lowest", callback_data='5'),
                 types.InlineKeyboardButton(text="Low", callback_data='4'),
                 types.InlineKeyboardButton(text="Medium", callback_data='3'),
                 types.InlineKeyboardButton(text="High", callback_data='2'),
                 types.InlineKeyboardButton(text="Highest", callback_data='1'))
    bot.send_message(ID,'Выберите приоритет: ',reply_markup= keyboard)

###################################################### МЕТОД ДЛЯ УСТАНОВКИ ДАТЫ ##########################################################

def set_date(ID):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Пропустить", callback_data="SkipDate"),
                 types.InlineKeyboardButton(text="Добавить дату",callback_data="date"))
    bot.send_message(ID,'Устанавливать дату выполнения?',reply_markup= keyboard)

def add_date(message):
    try:
        date_message= message.text.split(".")
        date(int(date_message[2]), int(date_message[1]), int(date_message[0]))
    except:
        if message.text == '!Отменить постановку задачи':
            cancel(message,False)
        else:
            bot.send_message(message.chat.id,'Некорректно введена дата')
            set_date(message.chat.id)
    else:
        usersDict[message.chat.id].date = message.text
        add_issue(message.chat.id)

####################################################### МЕТОД ДОБАВЛЕНИЯ ЗАДАЧИ В ДЖИРА ##########################################################################

def add_issue(ID):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да, отправить задачу в Jira', callback_data='Send'),
                 types.InlineKeyboardButton(text='Нет, выбрать редактируемые поля', callback_data='Edit'))
    bot.send_message(ID, f'1.Тема: {usersDict[ID].summary}' +
                                    f'\n2.Описание: {usersDict[ID].description[:-1]}' +
                                    f'\n3.Тип: {usersDict[ID].issue_type}' +
                                    f'\n4.Исполнитель: {usersDict[ID].assigneeID_assigneName[1]}' +
                                    f'\n5.Приоритет: {priorityDict.get(usersDict[ID].priority)}' + 
                                    f'\n6.Срок выполнения: {usersDict[ID].date}' + 
                                    f'\nКоличество прикреплённых файлов: {count_files(ID)}')
    bot.send_message(ID,"Данные введены верно?", reply_markup= keyboard)

################################################### МЕТОД ДЛЯ ОБРАБОТКИ CALLBACK ДАННЫХ #########################################

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data in usersDict[call.message.chat.id].issue_types:
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id, 
                                  text=f'Вы выбрали тип {call.data}.')
            usersDict[call.message.chat.id].issue_type = call.data
            if usersDict[call.message.chat.id].edit:
                add_issue(call.message.chat.id)
            else:
                set_assignee(call.message.chat.id)

        elif call.data == 'assigneeMe':
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id, 
                                  text=f'Исполнитель: {usersDict[call.message.chat.id].accountId_DisplayName[1]}.')
            usersDict[call.message.chat.id].assigneeID_assigneName = usersDict[call.message.chat.id].accountId_DisplayName
            if usersDict[call.message.chat.id].edit:
                add_issue(call.message.chat.id)
            else:
                set_priority(call.message.chat.id)
        elif call.data == 'assignee':
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id, 
                                  text='Введите полное имя исполнителя.')
            bot.register_next_step_handler(call.message,get_assignee)

        elif call.data.isnumeric():
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id, 
                                  text=f'Приоритет: {priorityDict.get(call.data)}.')
            usersDict[call.message.chat.id].priority = call.data
            if usersDict[call.message.chat.id].edit:
                add_issue(call.message.chat.id)
            else:
                set_date(call.message.chat.id)

        elif call.data == 'SkipDate':
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id, 
                                  text='Без даты')
            usersDict[call.message.chat.id].date = 'Без даты'
            add_issue(call.message.chat.id)
        elif call.data == 'date':
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id, 
                                  text='Введите дату выполнения в формате ДД.ММ.ГГГГ')
            bot.register_next_step_handler(call.message,add_date)

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
                                  text="Введите номер редактируемого элемента")
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= keyboard_edit_element())
            usersDict[call.message.chat.id].edit = True

        elif call.data == 'EditSummary':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            bot.register_next_step_handler(call.message, set_summary)
            bot.send_message(call.message.chat.id,'Введите тему задачи')
        elif call.data == 'EditDescription':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            usersDict[call.message.chat.id].description = ''
            bot.register_next_step_handler(call.message, set_description)
            bot.send_message(call.message.chat.id,
                             'введите описание, после чего нажмите кнопку \n!Завершить редактирование описания',
                             reply_markup= keyboard_edit_description())
        elif call.data == 'EditTypeIssue':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            set_issue_type(call.message.chat.id)
        elif call.data == 'EditAssignee':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            set_assignee(call.message.chat.id)
        elif call.data == 'EditPriority':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            set_priority(call.message.chat.id)
        elif call.data == 'EditDate':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            set_date(call.message.chat.id)
        elif call.data == 'back':
            bot.edit_message_reply_markup(call.message.chat.id, message_id= call.message.message_id, reply_markup= None)
            add_issue(call.message.chat.id)
            
######################################################### ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ########################################################

def count_files(id):
    result = len(glob.glob('bot\\descriptions\\' + str(id) + '_attacments\\*'))
    return str(result)


def keyboard_Cancel_issue():
    markup_reply = types.ReplyKeyboardMarkup(one_time_keyboard = False, resize_keyboard = True)
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
    markup_reply.add(types.KeyboardButton(text = '!Завершить редактирование описания'))
    return markup_reply

def keyboard_description():
    markup_reply = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    item_add_issue = types.KeyboardButton(text = '!Поставить задачу')
    item_cancel_issue = types.KeyboardButton(text = '!Отменить постановку задачи')

    markup_reply.add(item_add_issue,item_cancel_issue)
    return markup_reply

def delete_files(id):
    files = glob.glob('bot\\descriptions\\' + str(id) + '_attacments\\*')
    for f in files:
        os.remove(f)

def send_attachments(ID,issue):
    filesList=[]
    pathList=[]
    files = glob.glob('bot\\descriptions\\' + str(ID) + '_attacments\\*')
    for f in files:
        filesList.append(os.path.basename(f))
        pathList.append(f)
    for i in range(len(filesList)):
        add_attachments(usersDict[ID].email, usersDict[ID].password, issue, filesList[i], pathList[i])

def download_file(ID,file):
    file_info = bot.get_file(file.split('.')[0])
    downloaded_file = bot.download_file(file_info.file_path)
    src = 'bot\descriptions\\' + str(ID) + '_attacments\\' + file
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)

def cancel(message,send):
    usersDict[message.chat.id].summary = ''
    usersDict[message.chat.id].description = ''
    delete_files(message.chat.id)
    usersDict[message.chat.id].issue_type = ''
    usersDict[message.chat.id].assigneeID_assigneName = []
    usersDict[message.chat.id].priority = ''
    usersDict[message.chat.id].date = ''
    usersDict[message.chat.id].edit = False
    try:
        bot.edit_message_reply_markup(message.chat.id, message_id= message.message_id-1, reply_markup= None)
    except:
        pass
    if not send:
        bot.send_message(message.chat.id, 'Задача отменена', reply_markup= keyboard_description())

bot.polling(none_stop=True)