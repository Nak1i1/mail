# entrance.py
from password_bot import bot_token
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
from validate_email_address import validate_email
import imaplib

# Инициализация подключения к базе данных SQLite
connection = sqlite3.connect('users.db')
cursor = connection.cursor()

# Создание таблицы для хранения данных пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER PRIMARY KEY,
        email TEXT,
        password TEXT
    )
''')
connection.commit()

# Инициализация Telegram Bot
bot = telebot.TeleBot(bot_token)

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
        user_state[chat_id] = 'enter_password'
        bot.send_message(chat_id, 'Теперь введите пароль от вашей почты:')
    elif state == 'enter_password':
        # Извлечение почты и пароля из user_tokens
        email = user_state[chat_id]['email']
        password = message.text
        # Попытка входа в почтовый ящик пользователя
        try:
            mail = imaplib.IMAP4_SSL("imap.yandex.ru", port = 993)
            mail.login(email, password)
            # Если вход успешен, продолжаем мониторить ящик
            user_state.pop(chat_id) # Удаление состояния пользователя
            bot.send_message(chat_id, 'Успешно вошли в вашу почту. Теперь бот будет мониторить вашу почту.')
        except imaplib.IMAP4.error:
            # Если вход не удался, предложим пользователю повторить попытку
            bot.send_message(chat_id, 'Неверный адрес электронной почты или пароль. Пожалуйста, попробуйте еще раз.')
            user_state[chat_id] = 'enter_email'

bot.polling()
