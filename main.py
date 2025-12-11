import telebot
import requests, random
from telebot import types

bot = telebot.TeleBot("8583090175:AAHLKmKjPZQYmRiu-CTMG_5zYUDGjkf0qK0")
API_KEY = "34dff457cfc54fc5b8c3ce6204e7a701"

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
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)

    bot.send_message(message.chat.id, "Привет! Я бот новостей NewsBot\nВыберите команду:\n",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "get_news":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Ищу новости...")
        url = "https://newsapi.org/v2/everything"
        params ={
            "q": "новости",
            "apiKey": API_KEY,
            "language": "ru",
            "pageSize": 20}
        try:
            data = requests.get(url, params=params).json()
            articles = data.get("articles", [])

            if not articles:
                bot.send_message(call.message.chat.id, "Новостей не найдено")
                bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")
                return
            article = random.choice(articles)
            bot.send_message(call.message.chat.id, f"{article['title']}\n{article['url']}")
            bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")

        except Exception as e:
            bot.send_message(call.message.chat.id, f"Ошибка: {e}")
            bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")
    elif call.data == "choose_topic":
        bot.answer_callback_query(call.id)
        categories = ["business", "entertainment", "general","health", "science", "sports", "technology"]
        markup = types.InlineKeyboardMarkup()
        for cat in categories:
            markup.add(types.InlineKeyboardButton(cat.capitalize(), callback_data=f"cat_{cat}"))
        bot.send_message(call.message.chat.id,"Выберите категорию новостей:",reply_markup=markup)
    elif call.data.startswith("cat_"):
        bot.answer_callback_query(call.id)
        category = call.data.split("_")[1]
        url = "https://newsapi.org/v2/top-headlines"
        params ={
            "apiKey": API_KEY,
            "pageSize": 20,
            "category": category}
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
            "pageSize": 20}

        data = requests.get(url, params=params).json()
        articles = data.get("articles",[])
        if not articles:
            bot.send_message(call.message.chat.id, "Новостей не найдено")
            bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")
            return
        article = random.choice(articles)
        bot.send_message(call.message.chat.id, f"{article['title']}\n{article['url']}")
        bot.send_message(call.message.chat.id, "Нажмите /start чтобы вернуться в меню")    

    elif call.data == "search":
       bot.answer_callback_query(call.id)
       msg = bot.send_message(call.message.chat.id, f"Введите слово или фразу, по которой искать новости\n(Например: космос, еда и т.д.):")
       bot.register_next_step_handler(msg, search_news)

bot.infinity_polling()