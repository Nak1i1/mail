# Все библиотеки
pip install python-telegram-bot
pip install requests



# Плюсы:

1. Можно работать с данным ботом в своих личных целях, но кроме того можно использовать его как рабочий, то есть для всей корпорации. 

2. Более понятный интерфейс, чем у самого гмаила 

3. И так же по скорости он превышает работу гмайла. 

4. У обычного пользователя, использование почты более втопостпенна, в отличие от Телеграмма, Вконтакте и других.

5. Электронная почта один из самых используемых инструментов для обмена информацией, по этому данный бот сможет пользоваться популярностью при правильной рекламе

6. Использование нашего бота позволяет автоматизировать определенные задачи, управлять процессами и получать уведомления, что повышает эффективность работы с почтой


# Объяснение:

Этот бот нужен бля того, что бы легко и дотупно пользоваться почтой


































































import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests

bot = telebot.TeleBot('YOUR_BOT_TOKEN')

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(row_width=1)
    login_button = KeyboardButton('Войти')
    markup.add(login_button)
    bot.send_message(message.chat.id, 'Добро пожаловать! Нажмите кнопку "Войти", чтобы продолжить.', reply_markup=markup)

# Обработчик нажатия кнопки "Войти"
@bot.message_handler(func=lambda message: message.text == 'Войти')
def login(message):
    auth_url = 'https://oauth.yandex.ru/authorize?response_type=code&client_id=YOUR_CLIENT_ID'
    bot.send_message(message.chat.id, 'Авторизуйтесь, перейдя по ссылке: ' + auth_url)

# Обработчик получения кода авторизации от Яндекса
@bot.message_handler(func=lambda message: 'code=' in message.text)
def get_auth_code(message):
    code = message.text.split('code=')[1]
    # Запрос на получение токена доступа по коду авторизации
    token_params = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': 'YOUR_CLIENT_ID',
        'client_secret': 'YOUR_CLIENT_SECRET'
    }
    response = requests.post('https://oauth.yandex.ru/token', data=token_params)
    access_token = response.json()['access_token']
    
    # Получение пароля пользователя
    password = 'YOUR_PASSWORD'  # Здесь можно запросить пароль пользователя из базы данных или другого источника
    
    markup = ReplyKeyboardMarkup(row_width=1)
    send_button = KeyboardButton('Отправить')
    logout_button = KeyboardButton('Выйти из аккаунта')
    markup.add(send_button, logout_button)
    bot.send_message(message.chat.id, f'Вы успешно авторизованы! Ваш пароль: {password}', reply_markup=markup)

# Обработчик нажатия кнопки "Отправить"
@bot.message_handler(func=lambda message: message.text == 'Отправить')
def send_mail(message):
    bot.send_message(message.chat.id, 'Введите адрес получателя:')
    bot.register_next_step_handler(message, get_recipient)

def get_recipient(message):
    recipient = message.text
    bot.send_message(message.chat.id, 'Введите текст сообщения:')
    bot.register_next_step_handler(message, send_message, recipient)

def send_message(message, recipient):
    text = message.text
    
    # Отправка сообщения
    try:
        # Ваш код для отправки сообщения с использованием Яндекс.Почты API
        bot.send_message(message.chat.id, 'Успешно отправлено!')
    except:
        bot.send_message(message.chat.id, 'Произошла ошибка при отправке.')
        start(message)  # Возврат к началу

# Обработчик нажатия кнопки "Выйти из аккаунта"
@bot.message_handler(func=lambda message: message.text == 'Выйти из аккаунта')
def logout(message):
    start(message)  # Возврат к началу

bot.polling()








Конечно! Вот пояснения к каждой строке кода:

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
import time
Импортируем необходимые модули: telebot для работы с Telegram API, ReplyKeyboardMarkup и KeyboardButton для создания кнопок в интерфейсе бота, requests для выполнения HTTP-запросов, и time для управления временными задержками.
bot = telebot.TeleBot('YOUR_BOT_TOKEN')
Создаем экземпляр бота, указывая токен вашего бота, который вы получили от BotFather.
user_tokens = {}
Создаем пустой словарь user_tokens, который будет использоваться для хранения токенов доступа пользователей после авторизации.
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(row_width=1)
    login_button = KeyboardButton('Войти')
    markup.add(login_button)
    bot.send_message(message.chat.id, 'Добро пожаловать! Нажмите кнопку "Войти", чтобы продолжить.', reply_markup=markup)
Создаем обработчик команды /start, который отправляет приветственное сообщение с кнопкой "Войти".
@bot.message_handler(func=lambda message: message.text == 'Войти')
def login(message):
    auth_url = 'https://oauth.yandex.ru/authorize?response_type=code&client_id=YOUR_CLIENT_ID'
    bot.send_message(message.chat.id, 'Авторизуйтесь, перейдя по ссылке: ' + auth_url)
Создаем обработчик нажатия кнопки "Войти", который отправляет пользователю ссылку для авторизации на Яндексе через OAuth.
@bot.message_handler(func=lambda message: 'code=' in message.text)
def get_auth_code(message):
    code = message.text.split('code=')[1]
    token_params = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': 'YOUR_CLIENT_ID',
        'client_secret': 'YOUR_CLIENT_SECRET'
    }
    response = requests.post('https://oauth.yandex.ru/token', data=token_params)
    access_token = response.json().get('access_token')
Создаем обработчик получения кода авторизации, который отправляет запрос на получение токена доступа по коду авторизации и сохраняет токен доступа в словаре user_tokens.
def monitor_inbox(chat_id):
    while True:
        new_emails = check_new_emails(user_tokens[chat_id])
        if new_emails:
            for email in new_emails:
                bot.send_message(chat_id, f'Новое сообщение в вашей почте:\nОт: {email["from"]}\nТема: {email["subject"]}\n\n{email["snippet"]}')
        time.sleep(60)
Определяем функцию monitor_inbox, которая бесконечно проверяет почтовый ящик пользователя на наличие новых сообщений каждую минуту и отправляет уведомление, если такие сообщения найдены.
def check_new_emails(access_token):
    headers = {'Authorization': f'OAuth {access_token}'}
    response = requests.get('https://mail.yandex.ru/api/v2/mail/last', headers=headers)
    if response.status_code == 200:
        emails = response.json().get('messages', [])
        return emails
    return None
Определяем функцию check_new_emails, которая отправляет запрос к API Яндекс.Почты для проверки новых сообщений в почтовом ящике пользователя и возвращает список новых сообщений, если они есть.
@bot.message_handler(func=lambda message: message.text == 'Выйти из аккаунта')
def logout(message):
    if message.chat.id in user_tokens:
        del user_tokens[message.chat.id]
    start(message)
Создаем обработчик нажатия кнопки "Выйти из аккаунта", который удаляет токен доступа пользователя из словаря user_tokens и возвращает пользователя к начальному состоянию.
bot.polling()
Запускаем бота, начинаем прослушивание сообщений и обработку событий.




