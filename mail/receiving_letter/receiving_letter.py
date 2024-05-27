# receiving_letter.py
from bot.password_bot import bot_token
import telebot
import imaplib
import time
import sqlite3
import email
from email.header import Header
from validate_email_address import validate_email

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

# Словарь для хранения токенов пользователей
user_tokens = {}

# Словарь состояний для отслеживания процесса входа
user_state = {}

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
    result, data = mail.uid('search', None, "ALL") # Поиск всех писем
    if result == 'OK':
        for num in data[0].split():
            result, data = mail.uid('fetch', num, '(BODY.PEEK[HEADER])')
            if result == 'OK':
                raw_email = data[0][1].decode("utf-8") # Получение сырых данных письма
                email_message = email.message_from_string(raw_email)
                print(email_message['To'])
                print(email.utils.parseaddr(email_message['From'])) # Получение имени отправителя
                print(email_message.items()) # Вывод всех заголовков
                if email_message.is_multipart():
                    for part in email_message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            print(part.get_payload()) # Вывод текста письма
                else:
                    print(email_message.get_payload()) # Вывод текста письма
