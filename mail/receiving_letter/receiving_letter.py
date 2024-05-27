# receiving_letter.py
from password_bot import bot_token
import telebot
import imaplib
import time
import email
from email.header import decode_header
from validate_email_address import validate_email

# Инициализация Telegram Bot
bot = telebot.TeleBot(bot_token)

# Функция для мониторинга почтового ящика
def monitor_inbox(chat_id, mail):
    mail.select('inbox')
    while True:
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
    result, data = mail.uid('search', None, "UNSEEN")
    if result == 'OK':
        emails = []
        for num in data[0].split():
            result, data = mail.uid('fetch', num, '(BODY.PEEK[HEADER])')
            if result == 'OK':
                raw_email = data[0][1].decode("utf-8")
                email_message = email.message_from_string(raw_email)
                sender = decode_header(email_message['From'])[0][0]
                subject = decode_header(email_message['Subject'])[0][0]
                snippet = email_message.get_payload(decode=True).decode('utf-8')[:50]
                emails.append({"from": sender, "subject": subject, "snippet": snippet})
        return emails
    return None
