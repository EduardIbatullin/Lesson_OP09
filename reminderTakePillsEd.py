
import telebot
import datetime
import time
import threading
import random
from config import TOKEN  # Импортируем токен из конфигурационного файла

bot = telebot.TeleBot(TOKEN)  # Создаем экземпляр бота

# Словарь для хранения времени напоминаний для каждого пользователя
user_reminder_times = {}


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, 'Привет. Я чат-бот, который будет напоминать тебе принимать таблетки.')


# Обработчик команды /fact
@bot.message_handler(commands=['fact'])
def fact_message(message):
    try:
        with open('facts.txt', 'r', encoding='utf-8') as file:
            fact_list = file.readlines()
            random_fact = random.choice(fact_list).strip()
            bot.reply_to(message, f'{random_fact}')
    except FileNotFoundError:
        bot.reply_to(message, "Извините, не могу найти файл с фактами.")


# Обработчик команды /set_reminder
@bot.message_handler(commands=['set_reminder'])
def set_reminder(message):
    bot.reply_to(message, "Введите время в формате ЧЧ:ММ для установки напоминания:")
    bot.register_next_step_handler(message, process_reminder_time_input)


# Обработка введенного времени для установки напоминания
def process_reminder_time_input(message):
    try:
        # Парсим введенное время
        reminder_times = [datetime.datetime.strptime(t.strip(), "%H:%M").time() for t in message.text.split()]
        user_id = message.chat.id
        if user_id not in user_reminder_times:
            user_reminder_times[user_id] = []
        user_reminder_times[user_id].extend(reminder_times)  # Добавляем время напоминания для пользователя
        bot.send_message(user_id, f"Время напоминания успешно установлено на {', '.join(str(t.strftime('%H:%M')) for t in reminder_times)}.")
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат времени. Попробуйте еще раз.")


# Обработчик команды /cancel_reminder
@bot.message_handler(commands=['cancel_reminder'])
def cancel_reminder(message):
    user_id = message.chat.id
    if user_id in user_reminder_times:
        bot.reply_to(message, "Введите время в формате ЧЧ:ММ для отмены напоминания:")
        bot.register_next_step_handler(message, process_cancel_reminder_time_input)
    else:
        bot.send_message(user_id, "У вас нет установленных напоминаний.")


# Обработка введенного времени для отмены напоминания
def process_cancel_reminder_time_input(message):
    try:
        cancel_time = datetime.datetime.strptime(message.text.strip(), "%H:%M").time()
        user_id = message.chat.id
        if user_id in user_reminder_times:
            user_reminder_times[user_id] = [t for t in user_reminder_times[user_id] if t != cancel_time]
            bot.send_message(user_id, f"Напоминание на время {cancel_time.strftime('%H:%M')} успешно отменено.")
        else:
            bot.send_message(user_id, "У вас нет установленных напоминаний на это время.")
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат времени. Попробуйте еще раз.")


# Обработчик команды /show_reminders
@bot.message_handler(commands=['show_reminders'])
def show_reminders(message):
    user_id = message.chat.id
    if user_id in user_reminder_times:
        reminders = ', '.join(str(t.strftime('%H:%M')) for t in user_reminder_times[user_id])
        bot.send_message(user_id, f"Установленные напоминания: {reminders}")
    else:
        bot.send_message(user_id, "У вас нет установленных напоминаний.")


# Функция для отправки напоминаний
def send_reminders():
    while True:
        now = datetime.datetime.now().strftime("%H:%M")  # Получаем текущее время
        for user_id, reminder_times in user_reminder_times.items():
            for reminder_time in reminder_times:
                if now != reminder_time.strftime(
                        "%H:%M"):  # Проверяем совпадение времени напоминания и текущего времени
                    continue
                bot.send_message(user_id, f'Напоминаю! Текущее время {reminder_time.strftime("%H:%M")}. Вам пора принимать таблетки.')
                time.sleep(60)  # Подождать минуту, чтобы избежать множественных уведомлений
        time.sleep(1)  # Ждем 1 секунду перед следующей проверкой


# Запускаем поток для отправки напоминаний
threading.Thread(
    target=send_reminders,
    daemon=True  # Запускаем поток в "фоне"
    ).start()

bot.polling(none_stop=True)  # Запускаем бота, чтобы он ожидал новых сообщений


# Запускаем поток для отправки напоминаний
threading.Thread(
    target=send_reminders,
    daemon=True  # Запускаем поток в "фоне"
    ).start()

bot.polling(none_stop=True)  # Запускаем бота, чтобы он ожидал новых сообщений
