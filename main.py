import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os

# --- ЗМІННІ КОНФІГУРАЦІЇ ---
# BOT_TOKEN буде братися з оточення Render.com
BOT_TOKEN = os.getenv("BOT_TOKEN") 
# GROUP_CHAT_ID також рекомендується брати з оточення
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID") 

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {} # Словник для тимчасового зберігання даних користувача

def get_keyboard(step):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if step == 5:
        markup.add(KeyboardButton("Пропустити"))
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    user_data[chat_id] = {} # Очищаємо дані для нового замовлення
    bot.send_message(chat_id, "🟩 Вкажіть Ваше ім'я та прізвище:")
    bot.register_next_step_handler(message, process_name)

def process_name(message):
    chat_id = message.chat.id
    user_data[chat_id]["name"] = message.text
    bot.send_message(chat_id, "🟩 Вкажіть Ваш номер телефону:")
    bot.register_next_step_handler(message, process_phone)

def process_phone(message):
    chat_id = message.chat.id
    user_data[chat_id]["phone"] = message.text
    bot.send_message(chat_id, "🟩 Вкажіть артикул, розмір та кількість товару:")
    bot.register_next_step_handler(message, process_item_info)

def process_item_info(message):
    chat_id = message.chat.id
    user_data[chat_id]["item_info"] = message.text
    bot.send_message(chat_id, "🟩 Вкажіть місто/населений пункт та номер відділення Нової Пошти:")
    bot.register_next_step_handler(message, process_delivery)

def process_delivery(message):
    chat_id = message.chat.id
    user_data[chat_id]["delivery"] = message.text
    markup = get_keyboard(step=5)
    bot.send_message(chat_id,
        "🟩 У випадку передплати — надішліть скрін оплати товару на hotpicksua@gmail.com (Цей крок необов’язковий, лише якщо ви бажаєте оплатити наперед.)",
        reply_markup=markup)
    bot.register_next_step_handler(message, finalize_order)

def finalize_order(message):
    chat_id = message.chat.id
    # Обробити випадок, якщо користувач натиснув "Пропустити" або ввів щось інше
    user_data[chat_id]["prepay_info"] = message.text if message.text != "Пропустити" else "—"
    
    data = user_data[chat_id]
    order_text = (
        f"🟩 НОВЕ ЗАМОВЛЕННЯ\n\n"
        f"👤 Ім’я та прізвище: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"📦 Товар: {data['item_info']}\n"
        f"🚚 Доставка: {data['delivery']}\n"
        f"💳 Передплата: {data['prepay_info']}\n\n"
        f"🟢 Асортимент товарів та розмірна сітка:\n{os.getenv('ASSORTMENT_LINK', 'https://da.gd/b5tw')}\n\n"
        f"🟢 Політика конфіденційності, правила прийому та умови повернення товару:\n{os.getenv('PRIVACY_LINK', 'https://da.gd/hGajGc')}\n\n"
        f"⚠️ Оформлюючи замовлення, ви підтверджуєте, що ознайомлені з політикою конфіденційності, правилами отримання та умовами повернення товару."
    )
    
    # Відправка замовлення в адміністраторську групу
    bot.send_message(GROUP_CHAT_ID, order_text)
    
    # Повідомлення користувачу про успішне прийняття замовлення
    bot.send_message(chat_id, "✅ Дякуємо! Ваше замовлення прийнято. Менеджер зв’яжеться з вами найближчим часом для підтвердження.")

# --- ЗАПУСК БОТА ---
bot.polling()
