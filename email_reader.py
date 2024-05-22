import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
import time
import sqlite3

connection = sqlite3.connect('database_name.db')
bot = telebot.TeleBot('b8665d55475585291b5f17efa400647b')

# хранения токенов авторизации пользователей
user_tokens = {}

# /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(row_width=1)
    login_button = KeyboardButton('Войти')
    markup.add(login_button)
    bot.send_message(message.chat.id, 'Добро пожаловать! Нажмите кнопку "Войти", чтобы продолжить.', reply_markup=markup)

# "Войти"
@bot.message_handler(func=lambda message: message.text == 'Войти')
def login(message):
    auth_url = 'https://oauth.yandex.ru/authorize?response_type=code&client_id=YOUR_CLIENT_ID'    #Токен?, откуда
    bot.send_message(message.chat.id, 'Авторизуйтесь, перейдя по ссылке: ' + auth_url)

# Получение кода авторизации
@bot.message_handler(func=lambda message: 'code=' in message.text)
def get_auth_code(message):
    code = message.text.split('code=')[1]
    
    # Получение токена доступа с кода авторизации
    token_params = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': 'YOUR_CLIENT_ID',      
        'client_secret': 'YOUR_CLIENT_SECRET'   # Откуда
    }
    response = requests.post('https://oauth.yandex.ru/token', data=token_params)   # Как ?
    access_token = response.json().get('access_token')
    
    if access_token:
        # Хранение токена 
        user_tokens[message.chat.id] = access_token
        
        # мониторинг почтового ящика
        bot.send_message(message.chat.id, 'Вы успешно авторизованы! Теперь бот будет мониторить вашу почту.')
        monitor_inbox(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Ошибка при получении токена доступа.')

# мониторинга почтового ящика
def monitor_inbox(chat_id):
    while True:
        # проверка электронной post)
        new_emails = check_new_emails(user_tokens[chat_id])
        if new_emails:
            for email in new_emails:
                bot.send_message(chat_id, f'Новое сообщение в вашей почте:\nОт: {email["from"]}\nТема: {email["subject"]}\n\n{email["snippet"]}')
        time.sleep(60)  

# Проверка новый post
def check_new_emails(access_token):
    headers = {'Authorization': f'OAuth {access_token}'}
    response = requests.get('https://mail.yandex.ru/api/v2/mail/last', headers=headers)
    if response.status_code == 200:
        emails = response.json().get('messages', [])
        return emails
    return None

# Выйти из аккаунта
@bot.message_handler(func=lambda message: message.text == 'Выйти из аккаунта')
def logout(message):
    # Удалить токен доступ. пользователя
    if message.chat.id in user_tokens:
        del user_tokens[message.chat.id]
    start(message)

bot.polling()