<?php

// Конфигурационные данные для доступа к почтовому ящику
$email = 'your_email@example.com';
$password = 'your_email_password';

// Подключение к почтовому серверу
$inbox = imap_open('{imap.example.com:993/ssl}INBOX', $email, $password) or die('Не удалось подключиться к почтовому серверу: ' . imap_last_error());

// Получение списка сообщений
$emails = imap_search($inbox, 'ALL');

// Если есть новые сообщения
if ($emails) {
    // Перебор всех сообщений
    foreach ($emails as $email_number) {
        // Получение заголовков сообщения
        $headers = imap_headerinfo($inbox, $email_number);
        $from = $headers->fromaddress;
        $subject = $headers->subject;
        $date = $headers->date;

        // Получение текста сообщения
        $message = imap_fetchbody($inbox, $email_number, 1.1);

        // Отображение сообщения
        echo "From: $from<br>";
        echo "Subject: $subject<br>";
        echo "Date: $date<br>";
        echo "Message: $message<br>";
        echo "<hr>";
    }
} else {
    echo "Нет новых сообщений";
}

// Закрытие соединения с почтовым сервером
imap_close($inbox);
?>