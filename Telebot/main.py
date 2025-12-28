from telebot import TeleBot
import json
import sqlite3
from Parts.configserver import BOT_TOKEN

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
                answer_6 TEXT,    
                
            )
        """)
        conn.commit()

# Обработчик данных из WebApp
@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_webapp_data(message):
    try:
        # Парсим JSON из данных WebApp
        data = json.loads(message.web_app_data.data)
        print(data)

        user_id = data.get("userId")
        username = data.get("username")
        first_name = data.get("firstName")
        last_name = data.get("lastName")
        timestamp = data.get("timestamp")
        answers = data.get("answers", {})

        # Извлечение ответов (пример: у вас 3 вопроса)
        # Замените 'q1', 'q2', 'q3' на реальные ключи из data-question атрибутов
        answer_1 = answers.get("q1", "")
        answer_2 = answers.get("q2", "")
        answer_3 = answers.get("q3", "")
        answer_4 = answers.get("q4", "")
        answer_5 = answers.get("q5", "")
        answer_6 = answers.get("q6", "")

        # Проверка, существует ли уже пользователь
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM poll_responses WHERE user_id = ?", (user_id,))
            if cursor.fetchone() is not None:
                bot.send_message(
                    user_id,
                    "⚠️ Вы уже проходили этот опрос. Повторное участие невозможно."
                )
                return

            # Сохранение новых данных
            cursor.execute("""
                INSERT INTO poll_responses 
                (user_id, username, first_name, last_name, timestamp, answer_1, answer_2, answer_3, answer_4, answer_5, answer_6)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, first_name, last_name, timestamp, answer_1, answer_2, answer_3, answer_4, answer_5, answer_6))
            conn.commit()

        bot.send_message(user_id, "✅ Спасибо! Ваши ответы успешно сохранены.")

    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")
        bot.send_message(user_id, "❌ Произошла ошибка при сохранении данных. Обратитесь к администратору.")

# Обработка команды /start
@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        "Привет! Нажмите на кнопку ниже, чтобы пройти опрос.",
        reply_markup={
            "inline_keyboard": [[{
                "text": "📝 Пройти опрос",
                "web_app": {"url": "https://slerrick.github.io/TG_SchoolOne/"}  # ← Замените на реальный URL
            }]]
        }
    )

if __name__ == "__main__":
    init_db()
    print("Бот запущен...")
    bot.infinity_polling(none_stop=True)
