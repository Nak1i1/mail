import telebot


# Создание бота
bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_TOKEN')

# Словарь для отслеживания состояния пользователей
user_state = {}

# Функция для проверки формата адреса электронной почты
def validate_email(email):
    # Простейшая проверка формата адреса электронной почты с использованием регулярного выражения
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Функция для проверки доменного окончания адреса электронной почты
def check_email_domain(email):
    # Список допустимых доменных окончаний
    allowed_domains = ['yandex.ru', 'gmail.com', 'email.com']
    # Извлечение доменного окончания из адреса электронной почты
    domain = re.findall(r'@(.+)', email)
    if domain:
        domain = domain[0]
        if domain in allowed_domains:
            return True
    return False

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Привет! Для начала отправки писем введите свое имя:')
    # Установка состояния пользователя на 'enter_name'
    user_state[chat_id] = 'enter_name'

# Обработчик ввода пользователя во время ввода имени
@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id] == 'enter_name')
def handle_name(message):
    chat_id = message.chat.id
    user_name = message.text
    bot.send_message(chat_id, f'Привет, {user_name}! Теперь введите ваш адрес электронной почты:')
    # Установка состояния пользователя на 'enter_email'
    user_state[chat_id] = 'enter_email'

# Обработчик ввода пользователя во время ввода адреса электронной почты
@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id] == 'enter_email')
def handle_email(message):
    chat_id = message.chat.id
    user_email = message.text.lower()
    if not validate_email(user_email):
        bot.send_message(chat_id, 'Некорректный адрес электронной почты. Пожалуйста, введите корректный адрес.')
        return
    bot.send_message(chat_id, 'Введите пароль от вашей почты:')
    user_tokens[chat_id] = {'email': user_email}
    # Установка состояния пользователя на 'enter_password'
    user_state[chat_id] = 'enter_password'

# Обработчик ввода пользователя во время ввода пароля
@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id] == 'enter_password')
def handle_password(message):
    chat_id = message.chat.id
    user_password = message.text
    user_tokens[chat_id]['password'] = user_password
    bot.send_message(chat_id, 'Введите адрес электронной почты получателя:')
    # Установка состояния пользователя на 'enter_recipient_email'
    user_state[chat_id] = 'enter_recipient_email'

# Обработчик ввода пользователя во время ввода адреса получателя
@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id] == 'enter_recipient_email')
def handle_recipient_email(message):
    chat_id = message.chat.id
    recipient_email = message.text.lower()
    if not validate_email(recipient_email):
        bot.send_message(chat_id, 'Некорректный адрес электронной почты. Пожалуйста, введите корректный адрес почты получателя.')
        return
    if not check_email_domain(recipient_email):
        bot.send_message(chat_id, 'Недопустимый домен адреса электронной почты. Пожалуйста, используйте адрес с доменными окончаниями yandex.ru, gmail.com или email.com.')
        return
    user_tokens[chat_id]['recipient_email'] = recipient_email
    bot.send_message(chat_id, 'Введите текст вашего сообщения:')
    # Установка состояния пользователя на 'enter_message'
    user_state[chat_id] = 'enter_message'

# Обработчик ввода пользователя во время составления сообщения
@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id] == 'enter_message')
def handle_message(message):
    chat_id = message.chat.id
    sender_name = user_tokens[chat_id]['name']
    recipient_email = user_tokens[chat_id]['recipient_email']
    subject = f'Сообщение от {sender_name}'
    message_text = f'From: {sender_name}\n\n{message.text}'
    # Попытка отправить сообщение
    try:
        send_email(user_tokens[chat_id]['email'], user_tokens[chat_id]['password'], recipient_email, subject, message_text)
        bot.send_message(chat_id, 'Сообщение успешно отправлено!')
        user_state.pop(chat_id)  # Очистить состояние пользователя
    except Exception as e:
        bot.send_message(chat_id, f'Ошибка при отправке сообщения: {str(e)}')

# Запуск бота
bot.polling()