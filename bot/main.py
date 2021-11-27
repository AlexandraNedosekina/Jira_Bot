import telebot
from telebot import types
from config import tokenTg
from Jira_methods import *
import os, glob

bot = telebot.TeleBot(tokenTg)
class Data:
    email = ''
    password = ''
    accountId_DisplayName = []
    summary = ''
    issue_type = ''
    
    issue_types = []

    filesCount = 0

################################################################# РЕГИСТРАЦИЯ ###########################################################
@bot.message_handler(commands= 'start',content_types= 'text')
def start(message):
    bot.register_next_step_handler(message, get_email)
    bot.send_message(message.chat.id, "Введите вашу почту для регистрации.")
    
def get_email(message):
    Data.email = message.text
    bot.register_next_step_handler(message, data_verification)
    bot.send_message(message.chat.id, "Укажите API token.")

def data_verification(message):
    Data.password = message.text
    Data.accountId_DisplayName = authentication(Data.email, Data.password)
    if Data.accountId_DisplayName[0] == '401':
        bot.send_message(message.chat.id, "Данные введены не верно.")
        bot.send_message(message.chat.id, "Повторите попытку")
        start(message)
    else:
        with open("bot\\descriptions\\" + str(message.chat.id) + ".txt", "w",encoding="utf-8") as file:
#            file.write(Data.email + "," + Data.password + "," + Data.accountId + "\n")
            file.write('')
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
    if message.text == "!Поставить задачу":
        bot.register_next_step_handler(message, set_summary)
        bot.send_message(message.chat.id,'Введите тему задачи')
    elif message.text == "!Отменить постановку задачи":
        delete(message.chat.id)
    else:
        copy_description(message.text, message.chat.id)

####################################################### ЗАПОЛНЕНИЕ ОСТАЛЬНЫХ ПОЛЕЙ ######################################################

def set_summary(message):
    Data.summary = message.text
    set_issue_type(message.chat.id)

def set_issue_type(ID):
    keyboard = types.InlineKeyboardMarkup()
    Data.issue_types = get_issue_types(Data.email,Data.password)
    passed = False
    for i in range(len(Data.issue_types)):
        if passed:
            passed= False
        elif len(Data.issue_types) - i == 1:
            keyboard.add(types.InlineKeyboardButton(text=Data.issue_types[i], callback_data=Data.issue_types[i]))
        else:    
            keyboard.add(types.InlineKeyboardButton(text=Data.issue_types[i], callback_data=Data.issue_types[i]),
            types.InlineKeyboardButton(text=Data.issue_types[i + 1], callback_data=Data.issue_types[i + 1]))
            passed = True
    bot.send_message(ID,'Выберите тип задачи:', reply_markup= keyboard)

def set_assignee(ID):
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text='На меня', callback_data='assignee')
    keyboard.add(callback_button)
    bot.send_message(ID,'Введите Исполнителя.',reply_markup= keyboard)

################################################### МЕТОД ДЛЯ ОБРАБОТКИ CALLBACK ДАННЫХ #########################################

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data in Data.issue_types:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Вы выбрали тип {call.data}.')
            Data.typeissue = call.data
            set_assignee(call.message.chat.id)
        elif call.data == 'assignee'
            
######################################################### ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ########################################################
def keyboard_description():
    markup_reply = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    item_add_issue = types.KeyboardButton(text = '!Поставить задачу')
    item_cancel_issue = types.KeyboardButton(text = '!Отменить постановку задачи')

    markup_reply.add(item_add_issue,item_cancel_issue)
    return markup_reply

def copy_description(msg, id):
    with open("bot\\descriptions\\" + str(id) + ".txt", "a",encoding="utf-8") as file:
        file.write(msg + "\n")

def delete(id):
#    with open("bot\\descriptions\\" + str(id) + ".txt", "r",encoding="utf-8") as file:
#        text = file.read()    
    with open("bot\\descriptions\\" + str(id) + ".txt", "w",encoding="utf-8") as file:    
#        file.write(text.split('\n')[0] + '\n')
        file.write('')
    files = glob.glob('bot\\descriptions\\' + str(id) + '_attacments\\*')
    for f in files:
        os.remove(f)

def download_file(ID,file):
    file_info = bot.get_file(file.split('.')[0])
    downloaded_file = bot.download_file(file_info.file_path)
    src = 'bot\descriptions\\' + str(ID) + '_attacments\\' + file
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)

bot.polling(none_stop=True, interval=0,)