import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
import time
import sqlite3
import imaplib
import email
from email.header import decode_header
from validate_email_address import validate_email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Инициализация подключения к базе данных SQLite
connection = sqlite3.connect('database_name.db')
cursor = connection.cursor()

# Инициализация Telegram Bot
bot = telebot.TeleBot('ВАШ_ТОКЕН_ТЕЛЕГРАМ_БОТА')

# Словарь для хранения токенов пользователей
user_tokens = {}

# Словарь состояний для отслеживания процесса входа
user_state = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(row_width=1)
    login_button = KeyboardButton('Войти')
    compose_button = KeyboardButton('Написать сообщение')
    markup.add(login_button, compose_button)
    bot.send_message(message.chat.id, 'Добро пожаловать! Нажмите кнопку "Войти", чтобы продолжить.', reply_markup=markup)

# Обработчик кнопки "Войти"
@bot.message_handler(func=lambda message: message.text == 'Войти')
def login(message):
    bot.send_message(message.chat.id, 'Введите вашу почту:')
    # Установка состояния пользователя на 'enter_email'
    user_state[message.chat.id] = 'enter_email'

# Обработчик ввода пользователя во время процесса входа
@bot.message_handler(func=lambda message: message.chat.id in user_state)
def handle_login(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id)
    if state == 'enter_email':
        # Проверка корректности адреса электронной почты
        email = message.text.lower()
        if not validate_email(email):
            bot.send_message(chat_id, 'Некорректный адрес электронной почты. Пожалуйста, введите корректный адрес почты.')
            return
        user_tokens[chat_id] = {'email': email}
        user_state[chat_id] = 'enter_password'
        bot.send_message(chat_id, 'Теперь введите пароль от вашей почты:')
    elif state == 'enter_password':
        # Извлечение почты и пароля из user_tokens
        email = user_tokens[chat_id]['email']
        password = message.text
        # Попытка входа в почтовый ящик пользователя
        try:
            mail = imaplib.IMAP4_SSL("imap.yandex.ru")
            mail.login(email, password)
            # Если вход успешен, продолжаем мониторить ящик
            user_state.pop(chat_id)  # Удаление состояния пользователя
            monitor_inbox(chat_id, mail)
            bot.send_message(chat_id, 'Успешно вошли в вашу почту. Теперь бот будет мониторить вашу почту.')
        except imaplib.IMAP4.error:
            # Если вход не удался, предложим пользователю повторить попытку
            bot.send_message(chat_id, 'Неверный адрес электронной почты или пароль. Пожалуйста, попробуйте еще раз.')
            user_state[chat_id] = 'enter_email'

# Функция для мониторинга почтового ящика
def monitor_inbox(chat_id, mail):
    mail.select('inbox')
    while True:
        # Проверка новых сообщений
        new_emails = check_new_emails(mail)
        if new_emails:
            for email_data in new_emails:
                sender = email_data["from"]
                subject = email_data["subject"]
                snippet = email_data["snippet"]
                bot.send_message(chat_id, f'Новое сообщение в вашей почте:\nОт: {sender}\nТема: {subject}\n\n{snippet}')
        time.sleep(60)

# Функция для проверки новых сообщений
def check_new_emails(mail):
    headers = {'Authorization': f'OAuth {access_token}'}
    response = requests.get('https://mail.yandex.ru/api/v2/mail/last', headers=headers)
    if response.status_code == 200:
        emails = response.json().get('messages', [])
        return emails
    return None

# Обработчик команды "Выйти из аккаунта"
@bot.message_handler(func=lambda message: message.text == 'Выйти из аккаунта')
def logout(message):
    # Удаление токена доступа пользователя
    if message.chat.id in user_tokens:
        del user_tokens[message.chat.id]
    start(message)

# Обработчик кнопки "Написать сообщение"
@bot.message_handler(func=lambda message: message.text == 'Написать сообщение')
def compose_message(message):
    chat_id = message.chat.id
    if chat_id not in user_tokens:
        bot.send_message(chat_id, 'Для отправки сообщений необходимо авторизоваться. Нажмите "Войти", чтобы продолжить.')
        return
    bot.send_message(chat_id, 'Введите ваше имя:')
    # Установка состояния пользователя на 'enter_name'
    user_state[chat_id] = 'enter_name'

# Обработчик ввода пользователя во время составления сообщения
@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id] == 'enter_name')
def handle_name(message):
    chat_id = message.chat.id
    user_tokens[chat_id]['name'] = message.text
    bot.send_message(chat_id, 'Введите текст вашего сообщения:')
    # Установка состояния пользователя на 'enter_message'
    user_state[chat_id] = 'enter_message'

# Обработчик ввода пользователя во время составления сообщения
@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id] == 'enter_message')
def handle_message(message):
    chat_id = message.chat.id
    sender_name = user_tokens[chat_id]['name']
    recipient_email = 'ПОЧТА_ПОЛУЧАТЕЛЯ@example.com'  # Введите адрес электронной почты получателя здесь
    subject = f'Сообщение от {sender_name}'
    message_text = f'From: {sender_name}\n\n{message.text}'
    # Попытка отправить сообщение
    try:
        send_email(user_tokens[chat_id]['email'], message.text, recipient_email, subject, message_text)
        bot.send_message(chat_id, 'Сообщение успешно отправлено!')
        user_state.pop(chat_id)  # Очистить состояние пользователя
    except Exception as e:
        bot.send_message(chat_id, f'Ошибка при отправке сообщения: {str(e)}')

# Функция для отправки электронного сообщения
def send_email(sender_email, sender_password, recipient_email, subject, message_text):
    # Конфигурация SMTP
    smtp_server = 'smtp.yandex.ru'
    smtp_port = 465
    
    # Создание MIME-сообщения
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # Прикрепление текста сообщения
    msg.attach(MIMEText(message_text, 'plain'))
    
    # Создание SMTP-сессии
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

# Начать опрос для новых сообщений
bot.polling()