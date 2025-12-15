import telebot
import requests, random
from telebot import types
import sqlite3

bot = telebot.TeleBot("8583090175:AAHLKmKjPZQYmRiu-CTMG_5zYUDGjkf0qK0")
API_KEY = "34dff457cfc54fc5b8c3ce6204e7a701"
DIF_API_KEY = "43405c51b6e89cfdbc74d01fe57d02a2"

CATEGORIES =[
    "business",
    "entertainment",
    "health",
    "science",
    "sports",
    "technology"]
connect = sqlite3.connect("recomm.db", check_same_thread=False)
cursor = connect.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_recomm(
    user_id INTEGER,
    category TEXT,
    score INTEGER,
    PRIMARY KEY(user_id, category))""")
connect.commit()

def update_recomm(user_id, category, value):
    cursor.execute("""
    INSERT INTO user_recomm (user_id, category, score)
    VALUES (?, ?, ?)
    ON CONFLICT(user_id, category)
    DO UPDATE SET score = score + ? """,(user_id, category, value, value))
connect.commit()

def get_user_recomm(user_id):
    cursor.execute("""
    SELECT category, score
    FROM user_recomm
    WHERE user_id = ? AND score > 0""",(user_id,))
    return cursor.fetchall()
def choose_category(user_id):
    rec = get_user_recomm(user_id)
    if not rec:
        return None

    categories = []
    for category, score in rec:
        categories.extend([category] * score)

    return random.choice(categories)

def search_news(message):
       query = message.text.strip()
       url = "https://newsapi.org/v2/everything"
       params ={
           "q": query,
           "apiKey": API_KEY,
           "language": "ru",
           "sortBy": "publishedAt",
           "pageSize": 3}
       response = requests.get(url, params=params).json()
       if response.get("status") != "ok" or not response.get("articles"):
           bot.send_message(message.chat.id, "Новостей по этому запросу не найдено.")
           return
       for article in response["articles"]:
           bot.send_message(message.chat.id, f"{article['title']}\n{article['url']}")
       bot.send_message(message.chat.id, "Нажмите /start чтобы вернуться в меню")


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Получить случайную новость", callback_data="get_news")
    btn2 = types.InlineKeyboardButton("Выбрать тему", callback_data="choose_topic")
    btn3 = types.InlineKeyboardButton("Выбрать источник", callback_data="choose_source")
    btn4 = types.InlineKeyboardButton("Поиск новостей", callback_data= "search")
    btn5 = types.InlineKeyboardButton("Выбрать регион", callback_data= "choose_region")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)

    bot.send_message(message.chat.id, "Привет! Я бот новостей NewsBot\nВыберите команду:\n",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "get_news":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Ищу новости...")
        fav_category = choose_category(call.from_user.id)

        if fav_category and random.random() < 0.7:
            category = fav_category
        else:
            category = random.choice(CATEGORIES)
        url = "https://newsapi.org/v2/everything"
        params ={
            "apiKey": API_KEY,
            "q": category,
            "language": "ru",
            "sortBy": "publishedAt",
            "pageSize": 20}
        try:
            data = requests.get(url, params=params).json()
            articles = data.get("articles", [])

            if not articles:
                bot.send_message(call.message.chat.id, "Новостей не найдено")
                bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")
                return
            article = random.choice(articles)
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("👍", callback_data=f"like_{category}"),
                types.InlineKeyboardButton("👎", callback_data=f"dislike_{category}")
            )
            bot.send_message(call.message.chat.id, f"{article['title']}\n{article['url']}", reply_markup=markup)
            bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")

        except Exception as e:
            bot.send_message(call.message.chat.id, f"Ошибка: {e}")
            bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")
    elif call.data == "choose_topic":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup()
        for cat in CATEGORIES:
            markup.add(types.InlineKeyboardButton(cat.capitalize(), callback_data=f"cat_{cat}"))
        bot.send_message(call.message.chat.id,"Выберите категорию новостей:",reply_markup=markup)
    elif call.data.startswith("cat_"):
        bot.answer_callback_query(call.id)
        category = call.data.split("_")[1]
        url = "https://newsapi.org/v2/everything"
        params = {
            "apiKey": API_KEY,
            "q": category,
            "language": "ru",
            "sortBy": "publishedAt",
            "pageSize": 20}
        data = requests.get(url, params=params).json()
        articles = data.get("articles", [])
        if not articles:
            bot.send_message(call.message.chat.id, "Новостей не найдено")
            bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")
            return

        article = random.choice(articles)
        bot.send_message(call.message.chat.id,f"{article['title']}\n{article['url']}")
        bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")

    elif call.data == "choose_source":
        bot.answer_callback_query(call.id)
        url = "https://newsapi.org/v2/top-headlines/sources"
        params = {
            "apiKey": API_KEY,
            "language": "ru"
        }
        data = requests.get(url, params=params).json()
        sources = data.get("sources",[])
        if not sources:
            bot.send_message(call.message.chat.id, "Источники не найдены")
            bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")
            return
        markup = types.InlineKeyboardMarkup()
        for src in sources:
            sid = src["id"]
            name = src["name"]
            markup.add(types.InlineKeyboardButton(name, callback_data=f"src_{sid}"))
        bot.send_message(call.message.chat.id, "Выберите источник:", reply_markup=markup)
    elif call.data.startswith("src_"):
        bot.answer_callback_query(call.id)
        source = call.data.split("_", 1)[1]
        url = "https://newsapi.org/v2/top-headlines"
        params ={
            "apiKey": API_KEY,
            "sources": source,
            "pageSize": 20,
            "language": "ru"}

        data = requests.get(url, params=params).json()
        articles = data.get("articles",[])
        if not articles:
            bot.send_message(call.message.chat.id, "Новостей не найдено")
            bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")
            return
        article = random.choice(articles)
        bot.send_message(call.message.chat.id, f"{article['title']}\n{article['url']}")
        bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")    

    elif call.data.startswith("like_"):
        category = call.data.split("_")[1]
        update_recomm(call.from_user.id, category, +1)
        bot.answer_callback_query(call.id, "Буду показывать больше таких новостей")

    elif call.data.startswith("dislike_"):
        category = call.data.split("_")[1]
        update_recomm(call.from_user.id, category, -1)
        bot.answer_callback_query(call.id, "Буду показывать меньше таких новостей")

    elif call.data == "search":
       bot.answer_callback_query(call.id)
       msg = bot.send_message(call.message.chat.id, f"Введите слово или фразу, по которой искать новости\n(Например: космос, еда и т.д.):")
       bot.register_next_step_handler(msg, search_news)

    elif call.data == "choose_region":
        markup = types.InlineKeyboardMarkup()
        regions = {
            "Казахстан": "kz",
            "Россия": "ru",
            "США": "us",
            "Великобритания": "gb",
            "Германия": "de",
            "Франция": "fr",
            "Канада": "ca",
            "Австралия": "au",
            "Япония": "jp",
            "Украина": "ua"}
        for name, code in regions.items():
            markup.add(types.InlineKeyboardButton(name, callback_data=f"region_{code}"))
        bot.send_message(call.message.chat.id, "Выберите регион:", reply_markup=markup)

    elif call.data.startswith("region_"):
        bot.send_message(call.message.chat.id, "Ищу новости...")
        country = call.data.split("_")[1]
        url = "https://gnews.io/api/v4/top-headlines"
        params ={
            "apikey": DIF_API_KEY,
            "country": country,
            "lang": "ru",
            "max": 10}
        data = requests.get(url, params=params).json()
        articles = data.get("articles", [])
        if not articles:
            params["lang"] = "en"
            data = requests.get(url, params=params).json()
            articles = data.get("articles", [])
            if not articles:
                params["lang"] = "en"
                data = requests.get(url, params=params).json()
                articles = data.get("articles", [])
                if not articles:
                    bot.send_message(call.message.chat.id, "Новостей не найдено")
                    bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")
            return
        article = random.choice(articles)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("👍", callback_data=f"like_region_{country}"),
            types.InlineKeyboardButton("👎", callback_data=f"dislike_region_{country}")
        )
        bot.send_message(call.message.chat.id, f"{article['title']}\n{article['url']}", reply_markup=markup)
        bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")
bot.infinity_polling()
