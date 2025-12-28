from telebot import TeleBot, types
import json
import sqlite3
from Parts.configserver import BOT_TOKEN, ABOUT, INFO

# Инициализация бота
bot = TeleBot(BOT_TOKEN)

# Путь к базе данных
DB_NAME = "poll_results.db"

# Создание таблицы при запуске
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS poll_responses (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                timestamp TEXT,
                answer_1 TEXT,
                answer_2 TEXT,
                answer_3 TEXT,
                answer_4 TEXT,
                answer_5 TEXT,
                answer_6 TEXT
            )
        """)
        conn.commit()

# Обработчик данных из WebApp
@bot.message_handler(content_types=['web_app_data'])
def handle_webapp_data(message):
    try:
        # Парсим JSON из данных WebApp
        try:
            data = json.loads(message.web_app_data.data)
            print("Получены данные:", data)
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            bot.send_message(message.chat.id, "❌ Некорректные данные от WebApp.")
            return

        # Извлечение и валидация полей
        raw_user_id = message.from_user.id
        if not raw_user_id or not str(raw_user_id).isdigit():
            bot.send_message(message.chat.id, "❌ Некорректный идентификатор пользователя.")
            print(f"Некорректный userId: {raw_user_id}")
            return
        user_id = int(raw_user_id)

        username = data.get("username") or None
        first_name = data.get("firstName") or "Не указано"
        last_name = data.get("lastName") or "Не указано"
        timestamp = data.get("timestamp") or "Не указано"

        # Извлечение ответов
        questions_order = [
        'Самый/ая умный/ая',
        'Самый сильный',
        'Самая красивая',
        'Самый лучший класс',
        'Самый крутой учитель',
        'Человек года'
        ]

        # Извлечение ответов
        answers = [data['answers'][q] for q in questions_order]
        answer_1 = answers[0]
        answer_2 = answers[1]
        answer_3 = answers[2]
        answer_4 = answers[3]
        answer_5 = answers[4]
        answer_6 = answers[5]

        # Проверка, проходил ли пользователь опрос ранее
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM poll_responses WHERE user_id = ?", (user_id,))
            if cursor.fetchone() is not None:
                bot.send_message(
                    user_id,
                    "⚠️ Вы уже проходили этот опрос. Повторное участие невозможно."
                )
                print(f"Пользователь {user_id} пытался пройти опрос повторно.")
                return

            # Сохранение новых данных
            cursor.execute("""
                INSERT INTO poll_responses 
                (user_id, username, first_name, last_name, timestamp, answer_1, answer_2, answer_3, answer_4, answer_5, answer_6)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, first_name, last_name, timestamp,
                  answer_1, answer_2, answer_3, answer_4, answer_5, answer_6))
            conn.commit()

        bot.send_message(user_id, "✅ Спасибо! Ваши ответы успешно сохранены.")
        print(f"Опрос успешно сохранён для пользователя: {user_id}")

    except Exception as e:
        print(f"Неизвестная ошибка при обработке данных: {e}")
        try:
            bot.send_message(user_id, "❌ Произошла ошибка при сохранении данных. Обратитесь к администратору.")
        except:
            bot.send_message(message.chat.id, "❌ Ошибка обработки данных.")

# Обработка команды /start
@bot.message_handler(commands=["start"])
def start_handler(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(
        text="Открыть опрос",
        web_app=types.WebAppInfo(url="https://slerrick.github.io/TG_SchoolOne/")
    ))
    bot.send_message(
        message.chat.id,
        "Привет! Нажмите на кнопку ниже, чтобы пройти опрос.",
        reply_markup=keyboard
        
    )

@bot.message_handler(commands=["about"])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        ABOUT
    )

@bot.message_handler(commands=["info"])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        INFO
    )

if __name__ == "__main__":
    init_db()
    print("Бот запущен...")
    bot.infinity_polling(none_stop=True)
