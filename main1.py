import telebot
from telebot import types
from datetime import datetime, timedelta
import random
import time
import uuid
import threading
import json
import re

# --- КОНФІГУРАЦІЯ БОТА ТА ГЛОБАЛЬНІ ЗМІННІ ---
# ! ОБОВ'ЯЗКОВО ЗАПОВНІТЬ ЦІ ПОЛЯ СВОЇМИ ДАНИМИ !
BOT_TOKEN = "8464332909:AAHqGvVoPsFLhN2sY0pFzRoTV50PbFonvP8"
ADMIN_ID = "7853750281"  # ID адміністратора

# ID та посилання на обов'язкові канали
CHANNEL_1_ID_CHECK = "-1002876132664"
CHANNEL_1_URL = "https://t.me/SNOWstars_community"

# --- ДОДАНІ КАНАЛИ
CHANNEL_2_ID_CHECK = "-1002456211789"
CHANNEL_2_URL = "https://t.me/sosatwww"

CHANNEL_3_ID_CHECK = "-1002589787086"
CHANNEL_3_URL = "https://t.me/+QaJyLlc38JsxOTli"
# ------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)

# Константи для фінансових операцій
DEPOSIT_RATE_UAH_PER_PER_STAR = 0.87
WITHDRAW_RATE_UAH_PER_STAR = 0.77
DEPOSIT_REQUISITES = "IBAN_КАРТИ_АБО_ІНШІ_РЕКВІЗИТИ"
MIN_WITHDRAW_AMOUNT = 65
MIN_DEPOSIT_AMOUNT = 50
MIN_GAME_BET = 1

# Ціна та бонуси VIP-статусу
VIP_COST = 150.0
VIP_DAILY_BONUS_MULTIPLIER = 2.0
AD_DISCOUNT = 0.25
PROMO_CREATE_COST_MULTIPLIER = 0.8
REFERRAL_BONUS = 3.0
REFERRAL_EARNINGS_PERCENTAGE = 0.10

# Початкова ціна SNOW та його кількість
INITIAL_SNOW_PRICE = 3.0
INITIAL_SNOW_AVAILABLE = 1000.0

# Глобальні сховища даних
users = {}
pending_requests = {}
promos = {}
reviews = []
DICE_GAMES = {}
MINER_GAMES = {}
PLANE_GAMES = {}
user_orders = {}
market_data = {
    'market_price': INITIAL_SNOW_PRICE,
    'snow_available': INITIAL_SNOW_AVAILABLE,
    'is_open': True,
}

# Словник для множників Сапера (оновлено)
MINER_MULTIPLIERS = {
    5: [1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.0, 2.05],
    10: [1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.0, 2.05],
    15: [1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.0, 2.05],
    20: [1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.0, 2.05],
    24: [1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.0, 2.05]
}

# Додано для покрокового створення промокоду
admin_promo_creation_state = {}

# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def load_data():
    """Симулює завантаження даних із файлів."""
    global users, pending_requests, promos, reviews, user_orders, market_data
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            users_raw = json.load(f)
            users = {str(k): v for k, v in users_raw.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

    try:
        with open('requests.json', 'r', encoding='utf-8') as f:
            pending_requests = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pending_requests = {}

    try:
        with open('promos.json', 'r', encoding='utf-8') as f:
            promos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        promos = {}

    try:
        with open('reviews.json', 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
            if isinstance(reviews_data, list):
                reviews = reviews_data
            else:
                reviews = []
    except (FileNotFoundError, json.JSONDecodeError):
        reviews = []

    try:
        with open('orders.json', 'r', encoding='utf-8') as f:
            user_orders = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        user_orders = {}

    try:
        with open('market.json', 'r', encoding='utf-8') as f:
            file_content = f.read()
            if file_content:
                market_data.update(json.loads(file_content))
            else:
                print("Файл market.json порожній. Використовуємо значення за замовчуванням.")
    except (FileNotFoundError, json.JSONDecodeError):
        market_data = {
            'market_price': INITIAL_SNOW_PRICE,
            'snow_available': INITIAL_SNOW_AVAILABLE,
            'is_open': True,
        }

    # Скидаємо запити при завантаженні
    pending_requests = {}
    save_data()


def save_data():
    """Симулює збереження даних у файли."""
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)
    with open('requests.json', 'w', encoding='utf-8') as f:
        json.dump(pending_requests, f, indent=4, ensure_ascii=False)
    with open('promos.json', 'w', encoding='utf-8') as f:
        json.dump(promos, f, indent=4, ensure_ascii=False)
    with open('reviews.json', 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=4, ensure_ascii=False)
    with open('orders.json', 'w', encoding='utf-8') as f:
        json.dump(user_orders, f, indent=4, ensure_ascii=False)
    with open('market.json', 'w', encoding='utf-8') as f:
        json.dump(market_data, f, indent=4, ensure_ascii=False)


def safe_edit(text, chat_id, message_id, reply_markup=None, parse_mode=None):
    """
    Безпечна функція для редагування повідомлень.
    Повертає об'єкт повідомлення, або надсилає нове, якщо редагування неможливе.
    """
    try:
        return bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup, parse_mode=parse_mode)
    except telebot.apihelper.ApiException as e:
        if "message is not modified" in str(e):
            return None # Повертаємо None, якщо повідомлення не змінилося
        print(f"Помилка редагування: {e}")
        # Якщо сталася інша помилка (наприклад, повідомлення занадто старе), відправляємо нове
        try:
            bot.delete_message(chat_id, message_id)
        except telebot.apihelper.ApiException:
            pass # Повідомлення могло вже бути видалено
        return bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)


def escape_markdown(text):
    """Екранує спеціальні символи Markdown."""
    if text is None:
        return 'N/A'
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


def award_referer_earnings(user_id, amount):
    user_data = users.get(user_id)
    if user_data and 'referer' in user_data:
        referer_id = user_data['referer']
        referer_data = users.get(referer_id)
        if referer_data:
            earning = amount * REFERRAL_EARNINGS_PERCENTAGE
            referer_data['balance'] += earning
            save_data()
            try:
                bot.send_message(referer_id,
                                 f"🎉 Ваш реферал @{escape_markdown(user_data.get('username', 'N/A'))} заробив кошти, і ви отримали **{earning:.2f}⭐️** ({int(REFERRAL_EARNINGS_PERCENTAGE * 100)}% від заробітку)!",
                                 parse_mode="Markdown")
            except telebot.apihelper.ApiException:
                pass


def is_subscribed(user_id):
    """
    Перевіряє, чи підписаний користувач на всі обов'язкові канали.
    """
    return (is_subscribed_to_channel(user_id, CHANNEL_1_ID_CHECK) and
            is_subscribed_to_channel(user_id, CHANNEL_2_ID_CHECK) and
            is_subscribed_to_channel(user_id, CHANNEL_3_ID_CHECK))


def is_subscribed_to_channel(user_id, channel_id):
    """
    Перевіряє, чи підписаний користувач на конкретний канал.
    Бот повинен бути адміністратором в цьому каналі.
    """
    try:
        member = bot.get_chat_member(channel_id, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except telebot.apihelper.ApiException as e:
        print(f"Помилка при перевірці підписки: {e}")
        return False


def get_subscription_markup():
    """Генерує клавіатуру для перевірки підписки."""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➡️ Канал 1", url=CHANNEL_1_URL))
    markup.add(types.InlineKeyboardButton("➡️ Канал 2", url=CHANNEL_2_URL))
    markup.add(types.InlineKeyboardButton("➡️ Канал 3", url=CHANNEL_3_URL))
    markup.add(types.InlineKeyboardButton("✅ Я підписався", callback_data="check_subscription"))
    return markup


def get_main_reply_markup():
    """Генерує головну Reply-клавіатуру."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🏠 Меню")
    return markup


def get_cancel_inline_markup():
    """Генерує інлайн-клавіатуру для скасування."""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Скасувати", callback_data="cancel"))
    return markup


def get_main_inline_markup(user_id):
    """Генерує головне меню."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("👤 Профіль", callback_data="profile"),
               types.InlineKeyboardButton("🏆 Топ 10", callback_data="top10"))
    markup.add(types.InlineKeyboardButton("🎮 Ігри", callback_data="games"),
               types.InlineKeyboardButton("🎁 Щоденний бонус", callback_data="daily_bonus"))
    markup.add(types.InlineKeyboardButton("👥 Реферали", callback_data="referral"),
               types.InlineKeyboardButton("📈 Інвестиції", callback_data="crypto_investments"))
    if str(user_id) == str(ADMIN_ID):
        markup.add(types.InlineKeyboardButton("🔐 Адмін-панель", callback_data="admin_panel"))
    return markup


def show_main_menu(user_id, chat_id, message_id=None):
    """
    Відображає головне меню.
    Змінено, щоб відправляти/редагувати одне повідомлення.
    """
    user_data = users.get(str(user_id), {})
    username = escape_markdown(user_data.get('username', 'N/A'))

    menu_text = f"Вітаємо, **{username}**! 👋\nВаш баланс: **{user_data.get('balance', 0):.2f} ⭐**\nОберіть, що ви хочете зробити:"

    markup = get_main_inline_markup(user_id)
    if message_id:
        safe_edit(menu_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, menu_text, reply_markup=markup, parse_mode="Markdown")


def show_admin_market_manage(chat_id, message_id):
    """
    Відображає меню керування ринком SNOW для адміністратора.
    """
    market_status = "активний" if market_data.get('is_open', True) else "вимкнений"
    manage_text = f"📈 **Управління ринком SNOW**\n\n"
    manage_text += f"Поточний статус: **{market_status}**\n"
    manage_text += f"Ринкова ціна: **{market_data.get('market_price', INITIAL_SNOW_PRICE):.2f}⭐️**\n"
    manage_text += f"Доступно SNOW: **{market_data.get('snow_available', 0.0):.2f}❄️**\n\n"
    manage_text += "Оберіть дію:"

    markup = types.InlineKeyboardMarkup(row_width=2)
    if market_data.get('is_open', True):
        markup.add(types.InlineKeyboardButton("⏸ Вимкнути ринок", callback_data="admin_market_toggle"))
    else:
        markup.add(types.InlineKeyboardButton("▶️ Увімкнути ринок", callback_data="admin_market_toggle"))
    markup.add(types.InlineKeyboardButton("✏️ Змінити ціну", callback_data="admin_set_market_price"))
    markup.add(types.InlineKeyboardButton("➕ Додати SNOW", callback_data="admin_add_snow"))
    markup.add(types.InlineKeyboardButton("🔙 Адмін-панель", callback_data="admin_panel"))
    safe_edit(manage_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")


def show_admin_panel(user_id, chat_id, message_id=None):
    pending_deposits = [req for req in pending_requests.values() if req.get('type') == 'deposit' and req.get('status') == 'pending']
    pending_withdraws = [req for req in pending_requests.values() if req.get('type') == 'withdraw' and req.get('status') == 'pending']

    admin_text = "🔐 **Адмін-панель**\n\n"
    
    admin_text += "Оберіть дію:"
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(types.InlineKeyboardButton(f"💳 Обробка поповнень ({len(pending_deposits)})", callback_data="admin_deposit_requests_list"))
    markup.add(types.InlineKeyboardButton(f"💸 Обробка виведення ({len(pending_withdraws)})", callback_data="admin_withdraw_requests_list"))

    # Змінено: перенаправлення на новий покроковий процес
    markup.add(types.InlineKeyboardButton("🎁 Створити промокод", callback_data="admin_create_promo_step1"))
    markup.add(types.InlineKeyboardButton("👥 Список користувачів", callback_data="admin_show_users_0"))
    markup.add(types.InlineKeyboardButton("💰 Керування балансом", callback_data="admin_manage_balance"))
    markup.add(types.InlineKeyboardButton("📣 Розсилка", callback_data="admin_broadcast"))
    markup.add(types.InlineKeyboardButton("📈 Управління ринком", callback_data="admin_market_manage"))
    markup.add(types.InlineKeyboardButton("🏆 Топ 15 реферерів", callback_data="admin_top_referrers"))
    markup.add(types.InlineKeyboardButton("🔙 Головна", callback_data="main_menu"))
    if message_id:
        safe_edit(admin_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, admin_text, reply_markup=get_main_reply_markup(), parse_mode="Markdown")


def show_deposit_requests_list(chat_id, message_id):
    pending_deposits = [req for req in pending_requests.values() if req.get('type') == 'deposit' and req.get('status') == 'pending']
    
    if not pending_deposits:
        text = "✅ Наразі немає жодних запитів на поповнення."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Адмін-панель", callback_data="admin_panel"))
        safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        return

    text = "💳 **Запити на поповнення:**\n\n"
    markup = types.InlineKeyboardMarkup()
    
    for i, req in enumerate(pending_deposits):
        request_id = req.get('request_id', 'N/A')
        username = req.get('username', 'N/A')
        amount = req.get('amount', 0)
        text += f"**{i+1}.** @{escape_markdown(username)} - {amount:.2f}⭐️\n"
        markup.add(types.InlineKeyboardButton(f"▶️ Запит #{i+1}", callback_data=f"admin_view_deposit_{request_id}"))
    
    markup.add(types.InlineKeyboardButton("🔙 Адмін-панель", callback_data="admin_panel"))
    safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")


def show_withdraw_requests_list(chat_id, message_id):
    pending_withdraws = [req for req in pending_requests.values() if req.get('type') == 'withdraw' and req.get('status') == 'pending']
    
    if not pending_withdraws:
        text = "✅ Наразі немає жодних запитів на виведення."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Адмін-панель", callback_data="admin_panel"))
        safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        return

    text = "💸 **Запити на виведення:**\n\n"
    markup = types.InlineKeyboardMarkup()
    
    for i, req in enumerate(pending_withdraws):
        request_id = req.get('request_id', 'N/A')
        username = req.get('username', 'N/A')
        amount = req.get('amount', 0)
        text += f"**{i+1}.** @{escape_markdown(username)} - {amount:.2f}⭐️\n"
        markup.add(types.InlineKeyboardButton(f"▶️ Запит #{i+1}", callback_data=f"admin_view_withdraw_{request_id}"))
        
    markup.add(types.InlineKeyboardButton("🔙 Адмін-панель", callback_data="admin_panel"))
    safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

def show_users_list(chat_id, message_id, page):
    users_list = sorted(users.values(), key=lambda x: (x.get('username') or 'z').lower())
    page_size = 10
    total_pages = (len(users_list) + page_size - 1) // page_size
    start_index = page * page_size
    end_index = start_index + page_size
    current_page_users = users_list[start_index:end_index]
    
    if not current_page_users:
        text = "❌ Користувачів не знайдено."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Адмін-панель", callback_data="admin_panel"))
        safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        return
        
    text = f"👥 **Список користувачів (Сторінка {page + 1}/{total_pages})**\n\n"
    for i, user_data in enumerate(current_page_users):
        username = user_data.get('username', 'N/A')
        balance = user_data.get('balance', 0)
        is_vip = "👑" if user_data.get('is_vip') else ""
        text += f"**{start_index + i + 1}.** @{escape_markdown(username)} {is_vip} - **{balance:.2f} ⭐**\n"
        
    markup = types.InlineKeyboardMarkup(row_width=3)
    if page > 0:
        markup.add(types.InlineKeyboardButton("⬅️ Попередня", callback_data=f"admin_show_users_{page - 1}"))
    if page < total_pages - 1:
        markup.add(types.InlineKeyboardButton("Наступна ➡️", callback_data=f"admin_show_users_{page + 1}"))
    markup.add(types.InlineKeyboardButton("🔙 Адмін-панель", callback_data="admin_panel"))
    
    safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")


def show_profile_menu(user_id, chat_id, message_id):
    """
    Відображає меню профілю користувача.
    """
    user_data = users.get(str(user_id), {})
    username = escape_markdown(user_data.get('username', 'N/A'))
    user_id_int = user_data.get('id', 'N/A')
    balance = user_data.get('balance', 0)
    snow_balance = user_data.get('snow_balance', 0)
    is_vip = user_data.get('is_vip', False)
    vip_status = "✅ Активний" if is_vip else "❌ Неактивний"

    profile_text = (f"👤 **Профіль користувача**\n\n"
                    f"**Ваш ID:** `{user_id_int}`\n"
                    f"**Ваш нікнейм:** @{username}\n"
                    f"**Баланс:** `{balance:.2f} ⭐`\n"
                    f"**SNOW-баланс:** `{snow_balance:.2f} ❄️`\n"
                    f"**VIP-статус:** {vip_status}\n\n"
                    f"Оберіть дію:")

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("💰 Поповнити", callback_data="deposit"),
               types.InlineKeyboardButton("💸 Вивести", callback_data="withdraw"))
    
    if not is_vip:
        markup.add(types.InlineKeyboardButton("👑 Купити VIP-статус", callback_data="buy_vip"))
    
    # Додано кнопку "Промокод"
    markup.add(types.InlineKeyboardButton("🎁 Промокод", callback_data="promo_menu"))

    markup.add(types.InlineKeyboardButton("📜 Відгуки", callback_data="reviews"),
               types.InlineKeyboardButton("📝 Інструкція", callback_data="instructions"))
    
    markup.add(types.InlineKeyboardButton("🔙 Головна", callback_data="main_menu"))
    
    safe_edit(profile_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")


def show_reviews(user_id, chat_id, message_id):
    """Відображає відгуки користувачів з нумерацією."""
    reviews_list = sorted(reviews, key=lambda x: x.get('timestamp', '1970-01-01'), reverse=True)

    if not reviews_list:
        reviews_text = "📜 **Відгуки**\n\nЩе ніхто не залишив відгук. Будьте першим!"
    else:
        reviews_text = "📜 **Відгуки**\n\n"
        for i, review in enumerate(reviews_list):
            try:
                review_date = datetime.fromisoformat(review.get('timestamp', '')).strftime('%d.%m.%Y %H:%M')
            except ValueError:
                review_date = 'N/A'
            reviews_text += f"**{i + 1}**. \n💬 **@{escape_markdown(review.get('username', 'N/A'))}:**\n_{escape_markdown(review['text'])}_\n`{review_date}`\n\n"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✍️ Залишити відгук", callback_data="leave_review"))
    if str(user_id) == str(ADMIN_ID):
        markup.add(types.InlineKeyboardButton("❌ Видалити відгук", callback_data="admin_delete_review_menu"))

    markup.add(types.InlineKeyboardButton("🔙 Профіль", callback_data="profile"))

    safe_edit(reviews_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")


def show_instructions(user_id, chat_id, message_id):
    """Відображає інструкцію з використання бота."""
    instructions_text = (
        "📝 **Інструкція з використання бота**\n\n"
        "**1. Меню:**\n"
        " - **👤 Профіль:** Переглядайте ваш баланс, купуйте VIP-статус, поповнюйте та виводьте кошти.\n"
        " - **🏆 Топ 10:** Переглядайте рейтинг користувачів за балансом.\n"
        " - **🎮 Ігри:** Беріть участь у міні-іграх, таких як Кістки, Сапер та Літаки, щоб заробити більше ⭐.\n"
        " - **🎁 Щоденний бонус:** Отримуйте щоденний бонус, який збільшується кожного дня.\n"
        " - **👥 Реферали:** Запрошуйте друзів за своїм унікальним посиланням та отримуйте бонуси.\n"
        " - **📈 Інвестиції:** Купуйте та продавайте токен SNOW на внутрішньому ринку.\n\n"
        "**2. Поповнення та виведення:**\n"
        " - Для поповнення натисніть кнопку '💰 Поповнити', введіть суму в UAH та слідуйте інструкціям.\n"
        " - Для виведення натисніть '💸 Вивести', вкажіть суму в ⭐ та реквізити для виплати.\n\n"
        "**3. Ігри:**\n"
        " - Перед початком гри введіть вашу ставку. Вигравайте, щоб помножити свій баланс!\n"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Профіль", callback_data="profile"))
    
    safe_edit(instructions_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")


def parse_amount(text):
    """
    Безпечно конвертує текст у float. Підтримує як крапку, так і кому як розділювач.
    Повертає float або None у разі помилки.
    """
    try:
        cleaned_text = text.replace(',', '.').strip()
        if cleaned_text.endswith('.'):
            cleaned_text = cleaned_text[:-1]
        
        if not re.match(r'^-?\d+(\.\d+)?$', cleaned_text):
            return None
            
        return float(cleaned_text)
    except (ValueError, TypeError):
        return None

def find_user_by_id_or_username(query):
    """
    Знаходить користувача за ID або username.
    """
    if query in users:
        return query
    
    cleaned_query = query.lower().strip().replace('@', '')
    for user_id, user_data in users.items():
        if (user_data.get('username') or '').lower() == cleaned_query:
            return user_id
    
    return None


def get_top_referer_username():
    """
    Знаходить користувача, який запросив найбільше людей, і повертає його @username.
    """
    referer_counts = {}
    for user_data in users.values():
        referer_id = user_data.get('referer')
        if referer_id:
            referer_counts[referer_id] = referer_counts.get(referer_id, 0) + 1

    if not referer_counts:
        return None

    top_referer_id = max(referer_counts, key=referer_counts.get)
    top_referer_data = users.get(top_referer_id)
    if top_referer_data:
        return top_referer_data.get('username', None)
    return None


def create_miner_game(user_id, bet, mines_count):
    """Створює нову гру Сапер."""
    board_size = 5
    board = [[' ' for _ in range(board_size)] for _ in range(board_size)]
    mines = random.sample(range(board_size * board_size), mines_count)
    for i in mines:
        row, col = divmod(i, board_size)
        board[row][col] = '💣'

    MINER_GAMES[user_id] = {
        'bet': bet,
        'mines_count': mines_count,
        'board_size': board_size,
        'board': board,
        'revealed': [[False for _ in range(board_size)] for _ in range(board_size)],
        'steps': 0
    }
    return MINER_GAMES[user_id]


def get_miner_markup(user_id):
    """Генерує клавіатуру для гри в Сапер."""
    game = MINER_GAMES.get(user_id)
    if not game:
        return None

    markup = types.InlineKeyboardMarkup(row_width=game['board_size'])
    
    for row_index, row in enumerate(game['board']):
        row_buttons = []
        for col_index, cell in enumerate(row):
            button_text = "❓"
            if game['revealed'][row_index][col_index]:
                if cell == '💣':
                    button_text = '💣'
                else:
                    button_text = "✅"
                row_buttons.append(types.InlineKeyboardButton(button_text, callback_data="miner_noop"))
            else:
                row_buttons.append(types.InlineKeyboardButton(button_text, callback_data=f"miner_click_{row_index}_{col_index}"))
        markup.add(*row_buttons)

    multiplier_list = MINER_MULTIPLIERS.get(game['mines_count'], [])
    if game['steps'] < len(multiplier_list):
        current_multiplier = multiplier_list[game['steps']]
    else:
        current_multiplier = multiplier_list[-1] if multiplier_list else 1.0

    current_win = game['bet'] * current_multiplier

    if game['steps'] > 0:
        markup.add(types.InlineKeyboardButton(f"💸 Забрати виграш ({current_win:.2f}⭐️)", callback_data="miner_cashout"))
    markup.add(types.InlineKeyboardButton("❌ Вийти", callback_data="games"))
    return markup


# Змінена логіка гри "Літаки"
def start_plane_game(user_id, bet, message):
    game_state = {
        'bet': bet,
        'multiplier': 1.00,
        'message_id': message.message_id,
        'chat_id': message.chat.id,
        'running': True,
        'crash_chance_per_tick': 0.005 # Базовий шанс на краш за кожен тік
    }
    PLANE_GAMES[user_id] = game_state
    
    update_plane_message(user_id)

def update_plane_message(user_id):
    game_state = PLANE_GAMES.get(user_id)
    if not game_state or not game_state['running']:
        return

    # Динамічне збільшення шансу на краш
    current_crash_chance = game_state['crash_chance_per_tick'] * game_state['multiplier']
    
    if random.random() < current_crash_chance:
        game_state['running'] = False
        text = f"✈️ **Гра 'Літаки'**\n\n" \
               f"Літак розбився на множнику **x{game_state['multiplier']:.2f}**!\n" \
               f"Ваша ставка **{game_state['bet']:.2f}⭐️** згоріла. 😞"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎮 Знову грати", callback_data="game_plane"),
                   types.InlineKeyboardButton("🔙 Меню", callback_data="games"))
        safe_edit(text, game_state['chat_id'], game_state['message_id'], reply_markup=markup, parse_mode="Markdown")
        if user_id in PLANE_GAMES:
            del PLANE_GAMES[user_id]
        return

    game_state['multiplier'] += 0.01

    win_amount = game_state['bet'] * game_state['multiplier']

    text = f"✈️ **Гра 'Літаки'**\n\n" \
           f"Ставка: **{game_state['bet']:.2f}⭐️**\n" \
           f"Множник: **x{game_state['multiplier']:.2f}**\n" \
           f"Потенційний виграш: **{win_amount:.2f}⭐️**"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"💸 Забрати ({win_amount:.2f}⭐️)", callback_data="plane_cashout"))

    safe_edit(text, game_state['chat_id'], game_state['message_id'], reply_markup=markup, parse_mode="Markdown")

    timer = threading.Timer(0.7, update_plane_message, args=(user_id,))
    timer.start()

def show_investments_menu(user_id, chat_id, message_id):
    """Відображає меню інвестицій."""
    market = market_data.copy()
    market_price = market['market_price']
    snow_available = market['snow_available']
    is_open = market['is_open']
    
    status = "активний" if is_open else "закритий"

    invest_text = (f"📈 **Інвестиції SNOW**\n\n"
                   f"Поточний статус ринку: **{status}**\n"
                   f"Ціна 1 SNOW: **{market_price:.2f} ⭐**\n"
                   f"Доступно SNOW для купівлі: **{snow_available:.2f} ❄️**\n\n"
                   f"Ваш SNOW-баланс: **{users[str(user_id)]['snow_balance']:.2f} ❄️**\n"
                   f"Ваш баланс: **{users[str(user_id)]['balance']:.2f} ⭐**\n\n"
                   f"Оберіть дію:")

    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_open:
        markup.add(types.InlineKeyboardButton("Купити SNOW", callback_data="buy_snow"))
    markup.add(types.InlineKeyboardButton("🔙 Головна", callback_data="main_menu"))
    safe_edit(invest_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")


def show_daily_bonus_menu(user_id, chat_id, message_id):
    user_data = users.get(str(user_id), {})
    last_bonus_date_str = user_data.get('last_daily_bonus', '1970-01-01T00:00:00')
    last_bonus_date = datetime.fromisoformat(last_bonus_date_str)
    
    current_date = datetime.now()
    next_day_date = last_bonus_date + timedelta(days=1)
    
    # Оновлено, щоб щоденний бонус починався з 0.10 і збільшувався на 0.10
    bonus_amount = user_data.get('daily_bonus_amount', 0.10)
    
    text = "🎁 **Щоденний бонус**\n\n"
    markup = types.InlineKeyboardMarkup()
    
    if (current_date.date() - last_bonus_date.date()).days > 0:
        if bonus_amount > 1.0: # Скидаємо після досягнення 1.0
             user_data['daily_bonus_amount'] = 0.10
             bonus_amount = 0.10
             save_data()
        
        text += f"🎉 Ви можете отримати свій щоденний бонус: **{bonus_amount:.2f} ⭐**\n\n"
        markup.add(types.InlineKeyboardButton("🎉 Забрати бонус", callback_data=f"claim_daily_bonus_{bonus_amount}"))
    else:
        time_to_wait = next_day_date - current_date
        hours, remainder = divmod(time_to_wait.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        text += f"⏰ Ви вже отримали бонус за сьогодні.\n"
        text += f"Наступний бонус буде доступний через: **{hours:02}:{minutes:02}:{seconds:02}**"
    
    if user_data.get('daily_bonus_amount', 0.10) < 1.0:
        next_bonus_amount = min(user_data.get('daily_bonus_amount', 0.10) + 0.10, 1.0)
        text += f"\n\nБонус за завтра: **{next_bonus_amount:.2f} ⭐**"

    markup.add(types.InlineKeyboardButton("🔙 Головна", callback_data="main_menu"))
    safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")


# --- ОСНОВНІ ОБРОБНИКИ КОМАНД ТА ПОВІДОМЛЕНЬ ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    if not username:
        username = f"user_{user_id}"

    # Перевіряємо, чи існує користувач
    if user_id not in users:
        # Реєструємо нового користувача
        users[user_id] = {
            'id': user_id,
            'username': username,
            'balance': 0.0,
            'snow_balance': 0.0,
            'is_vip': False,
            'last_daily_bonus': '1970-01-01T00:00:00',
            'daily_bonus_amount': 0.10,
            'activated_promos': []
        }
        save_data()
        
        # Перевіряємо, чи є реферальне посилання
        ref_id_match = re.match(r'/start\s+(\d+)', message.text)
        if ref_id_match:
            referer_id = ref_id_match.group(1)
            if referer_id != user_id and referer_id in users:
                users[user_id]['referer'] = referer_id
                users[user_id]['balance'] += REFERRAL_BONUS
                users[referer_id]['balance'] += REFERRAL_BONUS
                save_data()
                bot.send_message(referer_id, f"🎉 Ваш реферал @{escape_markdown(username)} зареєструвався за вашим посиланням, і ви обидва отримали по **{REFERRAL_BONUS:.2f} ⭐**!", parse_mode="Markdown")
                bot.send_message(message.chat.id, f"🎉 Ви успішно зареєструвалися за реферальним посиланням і отримали **{REFERRAL_BONUS:.2f} ⭐**!", parse_mode="Markdown")
        
    if not is_subscribed(user_id):
        text = ("❗️ **Перед використанням бота, будь ласка, підпишіться на наші канали:**")
        bot.send_message(message.chat.id, text, reply_markup=get_subscription_markup(), parse_mode="Markdown")
    else:
        show_main_menu(user_id, message.chat.id)


@bot.message_handler(func=lambda message: message.text == "🏠 Меню")
def handle_menu_button(message):
    user_id = str(message.from_user.id)
    if not is_subscribed(user_id):
        text = ("❗️ **Перед використанням бота, будь ласка, підпишіться на наші канали:**")
        bot.send_message(message.chat.id, text, reply_markup=get_subscription_markup(), parse_mode="Markdown")
    else:
        show_main_menu(user_id, message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    data = call.data

    bot.answer_callback_query(call.id)
    
    if not is_subscribed(user_id):
        text = ("❗️ **Перед використанням бота, будь ласка, підпишіться на наші канали:**")
        safe_edit(text, chat_id, message_id, reply_markup=get_subscription_markup(), parse_mode="Markdown")
        return

    # --- ГОЛОВНЕ МЕНЮ ---
    if data == "main_menu":
        show_main_menu(user_id, chat_id, message_id)
    
    # --- ПРОФІЛЬ ---
    elif data == "profile":
        show_profile_menu(user_id, chat_id, message_id)

    # --- ПРОМОКОДИ (НОВЕ) ---
    elif data == "promo_menu":
        text = "🎁 **Промокоди**\n\nВведіть промокод, щоб отримати бонус:"
        sent_msg = safe_edit(text, chat_id, message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, process_promo_code, sent_msg)
        
    # --- ІНСТРУКЦІЯ ---
    elif data == "instructions":
        show_instructions(user_id, chat_id, message_id)

    # --- ВІДГУКИ ---
    elif data == "reviews":
        show_reviews(user_id, chat_id, message_id)
        
    elif data == "leave_review":
        text = "💬 **Напишіть ваш відгук:**"
        markup = types.ForceReply(selective=False)
        sent_msg = safe_edit(text, chat_id, message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_review, sent_msg)

    # --- ТОП 10 ---
    elif data == "top10":
        top_users = sorted(users.values(), key=lambda x: x.get('balance', 0), reverse=True)[:10]
        text = "🏆 **Топ 10 користувачів за балансом:**\n\n"
        for i, user_data in enumerate(top_users):
            username = escape_markdown(user_data.get('username', 'N/A'))
            balance = user_data.get('balance', 0)
            text += f"**{i+1}.** @{username} - **{balance:.2f} ⭐**\n"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Головна", callback_data="main_menu"))
        safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

    # --- ІГРИ ---
    elif data == "games":
        games_text = "🎮 **Ігровий зал**\n\nОберіть гру:"
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("🎲 Кістки", callback_data="game_dice"),
                   types.InlineKeyboardButton("⛏️ Сапер", callback_data="game_miner"))
        markup.add(types.InlineKeyboardButton("✈️ Літаки", callback_data="game_plane"),
                   types.InlineKeyboardButton("🔙 Головна", callback_data="main_menu"))
        safe_edit(games_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

    elif data == "game_dice":
        dice_text = "🎲 **Гра 'Кістки'**\n\nОберіть свій варіант:"
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("🟢 Парне", callback_data="dice_even"),
                   types.InlineKeyboardButton("🔴 Непарне", callback_data="dice_odd"))
        markup.add(types.InlineKeyboardButton("🔙 Ігри", callback_data="games"))
        safe_edit(dice_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

    elif data in ["dice_even", "dice_odd"]:
        choice = data.split('_')[1]
        text = f"🎲 Ви обрали **{'Парне' if choice == 'even' else 'Непарне'}**.\n\n" \
               f"Введіть суму ставки. Мінімальна ставка: **{MIN_GAME_BET} ⭐**."
        sent_msg = safe_edit(text, chat_id, message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_dice_bet, sent_msg, choice)

    elif data == "game_miner":
        miner_text = "⛏️ **Гра 'Сапер'**\n\nОберіть кількість мін:"
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(types.InlineKeyboardButton("5 мін", callback_data="miner_mines_5"),
                   types.InlineKeyboardButton("10 мін", callback_data="miner_mines_10"),
                   types.InlineKeyboardButton("15 мін", callback_data="miner_mines_15"))
        markup.add(types.InlineKeyboardButton("20 мін", callback_data="miner_mines_20"),
                   types.InlineKeyboardButton("24 міни", callback_data="miner_mines_24"))
        markup.add(types.InlineKeyboardButton("🔙 Ігри", callback_data="games"))
        safe_edit(miner_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

    elif data.startswith("miner_mines_"):
        mines_count = int(data.split('_')[2])
        text = f"⛏️ Ви обрали **{mines_count} мін**.\n\nВведіть суму ставки. Мінімальна ставка: **{MIN_GAME_BET} ⭐**."
        sent_msg = safe_edit(text, chat_id, message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_miner_bet, sent_msg, mines_count)
        
    elif data.startswith("miner_click_"):
        game = MINER_GAMES.get(user_id)
        if not game:
            safe_edit("❌ Гру не знайдено. Почніть нову.", chat_id, message_id, reply_markup=get_main_inline_markup(user_id))
            return
        
        row, col = map(int, data.split('_')[2:])
        
        if game['revealed'][row][col]:
            bot.answer_callback_query(call.id, "Ця клітинка вже відкрита.")
            return

        game['revealed'][row][col] = True
        
        if game['board'][row][col] == '💣':
            # Програш
            text = f"⛏️ **Гра 'Сапер'**\n\n" \
                   f"Ви відкрили міну! 💥\n" \
                   f"Ваша ставка **{game['bet']:.2f} ⭐** згоріла. 😞"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🎮 Знову грати", callback_data="game_miner"),
                       types.InlineKeyboardButton("🔙 Ігри", callback_data="games"))
            safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
            if user_id in MINER_GAMES:
                del MINER_GAMES[user_id]
            return
        else:
            # Виграш
            game['steps'] += 1
            multiplier_list = MINER_MULTIPLIERS.get(game['mines_count'], [])
            
            if game['steps'] <= len(multiplier_list):
                current_multiplier = multiplier_list[game['steps'] - 1]
            else:
                current_multiplier = multiplier_list[-1] if multiplier_list else 1.0

            win_amount = game['bet'] * current_multiplier
            
            # Перевіряємо, чи залишилися клітинки для відкриття
            total_cells = game['board_size'] * game['board_size']
            revealed_count = sum(row.count(True) for row in game['revealed'])
            
            if revealed_count == total_cells - game['mines_count']:
                users[user_id]['balance'] += win_amount
                save_data()
                text = f"🎉 **Вітаємо!** Ви відкрили всі безпечні клітинки і виграли!\n\n" \
                       f"Ви виграли: **{win_amount:.2f} ⭐**\n" \
                       f"Ваш новий баланс: **{users[user_id]['balance']:.2f} ⭐**"
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🎮 Знову грати", callback_data="game_miner"),
                           types.InlineKeyboardButton("🔙 Ігри", callback_data="games"))
                safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
                award_referer_earnings(user_id, win_amount - game['bet'])
                if user_id in MINER_GAMES:
                    del MINER_GAMES[user_id]
                return
            
            game_text = (f"⛏️ **Гра 'Сапер'**\n\n"
                         f"Ставка: **{game['bet']:.2f} ⭐**\n"
                         f"Кількість мін: **{game['mines_count']}**\n\n"
                         f"Поточний множник: **x{current_multiplier:.2f}**\n"
                         f"Потенційний виграш: **{win_amount:.2f} ⭐**\n\n"
                         f"Оберіть наступну клітинку:")
            
            safe_edit(game_text, chat_id, message_id, reply_markup=get_miner_markup(user_id), parse_mode="Markdown")
    
    elif data == "miner_cashout":
        game = MINER_GAMES.get(user_id)
        if not game:
            safe_edit("❌ Гру не знайдено. Почніть нову.", chat_id, message_id, reply_markup=get_main_inline_markup(user_id))
            return
            
        multiplier_list = MINER_MULTIPLIERS.get(game['mines_count'], [])
        if game['steps'] > 0 and game['steps'] <= len(multiplier_list):
            current_multiplier = multiplier_list[game['steps'] - 1]
            win_amount = game['bet'] * current_multiplier
            users[user_id]['balance'] += win_amount
            save_data()
            text = f"🎉 **Вітаємо!** Ви успішно забрали виграш!\n\n" \
                   f"Множник: **x{current_multiplier:.2f}**\n" \
                   f"Виграш: **{win_amount:.2f} ⭐**\n" \
                   f"Ваш новий баланс: **{users[user_id]['balance']:.2f} ⭐**"
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🎮 Знову грати", callback_data="game_miner"),
                       types.InlineKeyboardButton("🔙 Ігри", callback_data="games"))
            safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
            award_referer_earnings(user_id, win_amount - game['bet'])
        else:
            safe_edit("❌ Ви ще не відкрили жодної клітинки. Почніть гру.", chat_id, message_id, reply_markup=get_miner_markup(user_id))
            
        if user_id in MINER_GAMES:
            del MINER_GAMES[user_id]
        
    elif data == "game_plane":
        plane_text = "✈️ **Гра 'Літаки'**\n\n" \
                     "Введіть суму ставки. Мінімальна ставка: **{MIN_GAME_BET} ⭐**."
        sent_msg = safe_edit(plane_text, chat_id, message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_plane_bet, sent_msg)
    
    elif data == "plane_cashout":
        game = PLANE_GAMES.get(user_id)
        if not game:
            safe_edit("❌ Гру не знайдено. Почніть нову.", chat_id, message_id, reply_markup=get_main_inline_markup(user_id))
            return
            
        win_amount = game['bet'] * game['multiplier']
        users[user_id]['balance'] += win_amount
        save_data()
        
        text = f"🎉 **Вітаємо!** Ви успішно забрали виграш!\n\n" \
               f"Множник: **x{game['multiplier']:.2f}**\n" \
               f"Виграш: **{win_amount:.2f} ⭐**\n" \
               f"Ваш новий баланс: **{users[user_id]['balance']:.2f} ⭐**"
               
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎮 Знову грати", callback_data="game_plane"),
                   types.InlineKeyboardButton("🔙 Ігри", callback_data="games"))
                   
        safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        award_referer_earnings(user_id, win_amount - game['bet'])
        
        if user_id in PLANE_GAMES:
            del PLANE_GAMES[user_id]
            
    # --- ІНВЕСТИЦІЇ SNOW ---
    elif data == "crypto_investments":
        show_investments_menu(user_id, chat_id, message_id)

    elif data == "buy_snow":
        market = market_data.copy()
        if not market['is_open'] or market['snow_available'] <= 0:
            text = "❌ На жаль, ринок SNOW наразі закритий або закінчився."
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Інвестиції", callback_data="crypto_investments"))
            safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
            return
        
        price = market['market_price']
        text = (f"📈 **Купівля SNOW**\n\n"
                f"Поточна ціна: **1 SNOW = {price:.2f} ⭐**\n"
                f"Доступно: **{market['snow_available']:.2f} ❄️**\n\n"
                f"Ваш SNOW-баланс: **{users[str(user_id)]['snow_balance']:.2f} ❄️**\n"
                f"Ваш баланс: **{users[str(user_id)]['balance']:.2f} ⭐**\n\n"
                f"Введіть кількість SNOW, яку ви хочете купити:")
        
        sent_msg = safe_edit(text, chat_id, message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_buy_snow_amount, sent_msg)
    
    # --- ЩОДЕННИЙ БОНУС ---
    elif data == "daily_bonus":
        show_daily_bonus_menu(user_id, chat_id, message_id)
        
    elif data.startswith("claim_daily_bonus_"):
        bonus_amount_str = data.split('_')[3]
        bonus_amount = parse_amount(bonus_amount_str)
        
        user_data = users.get(user_id, {})
        last_bonus_date_str = user_data.get('last_daily_bonus', '1970-01-01T00:00:00')
        last_bonus_date = datetime.fromisoformat(last_bonus_date_str)
        
        current_date = datetime.now()
        
        if (current_date.date() - last_bonus_date.date()).days > 0:
            user_data['balance'] += bonus_amount
            user_data['last_daily_bonus'] = current_date.isoformat()
            
            # Збільшуємо бонус на 0.10, але не більше 1.0
            next_bonus_amount = min(bonus_amount + 0.10, 1.0)
            user_data['daily_bonus_amount'] = next_bonus_amount
            
            save_data()
            safe_edit(f"🎉 **Вітаємо!** Ви отримали свій щоденний бонус **{bonus_amount:.2f} ⭐**!", chat_id, message_id, reply_markup=get_main_inline_markup(user_id), parse_mode="Markdown")
        else:
            safe_edit("❌ Ви вже отримали бонус за сьогодні. Спробуйте завтра.", chat_id, message_id, reply_markup=get_main_inline_markup(user_id), parse_mode="Markdown")

    # --- РЕФЕРАЛИ ---
    elif data == "referral":
        user_data = users.get(user_id, {})
        ref_link = f"https://t.me/{(bot.get_me().username or 'N/A')}?start={user_id}"
        
        referer_count = sum(1 for u in users.values() if u.get('referer') == user_id)
        
        referral_text = (f"👥 **Реферальна програма**\n\n"
                         f"Запрошуйте друзів та отримуйте **{REFERRAL_BONUS:.2f} ⭐** за кожного!\n"
                         f"Ви також будете отримувати **{int(REFERRAL_EARNINGS_PERCENTAGE * 100)}%** від їх заробітку в іграх!\n\n"
                         f"Ваше унікальне посилання:\n`{ref_link}`\n\n"
                         f"Запрошено користувачів: **{referer_count}**\n\n"
                         f"Просто скопіюйте посилання і поділіться з друзями!")
                         
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Головна", callback_data="main_menu"))
        safe_edit(referral_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

    # --- VIP ---
    elif data == "buy_vip":
        user_data = users.get(user_id, {})
        if user_data.get('is_vip'):
            safe_edit("❌ У вас вже є VIP-статус.", chat_id, message_id, reply_markup=get_main_inline_markup(user_id))
            return
        
        text = (f"👑 **Покупка VIP-статусу**\n\n"
                f"Вартість VIP: **{VIP_COST:.2f} ⭐**\n\n"
                f"**Переваги VIP:**\n"
                f" - Щоденний бонус збільшується на **{int(VIP_DAILY_BONUS_MULTIPLIER)}x**\n"
                f" - Знижка на рекламу **{int(AD_DISCOUNT * 100)}%**\n"
                f" - Знижка на створення промокодів **{int((1 - PROMO_CREATE_COST_MULTIPLIER) * 100)}%**\n\n"
                f"Ви хочете купити VIP-статус?")
                
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("✅ Купити", callback_data="confirm_buy_vip"),
                   types.InlineKeyboardButton("❌ Скасувати", callback_data="profile"))
                   
        safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
    
    elif data == "confirm_buy_vip":
        user_data = users.get(user_id, {})
        if user_data.get('balance', 0) >= VIP_COST:
            user_data['balance'] -= VIP_COST
            user_data['is_vip'] = True
            save_data()
            safe_edit(f"🎉 **Вітаємо!** Ви успішно купили VIP-статус за **{VIP_COST:.2f} ⭐**.", chat_id, message_id, reply_markup=get_main_inline_markup(user_id), parse_mode="Markdown")
        else:
            safe_edit("❌ У вас недостатньо коштів для покупки VIP-статусу.", chat_id, message_id, reply_markup=get_main_inline_markup(user_id))
    
    # --- ФІНАНСОВІ ОПЕРАЦІЇ ---
    elif data == "deposit":
        text = (f"💰 **Поповнення балансу**\n\n"
                f"Курс: **1 ⭐ = {DEPOSIT_RATE_UAH_PER_PER_STAR:.2f} UAH**\n\n"
                f"Введіть суму поповнення в **UAH**. Мінімальна сума: **{MIN_DEPOSIT_AMOUNT} грн**.")
        sent_msg = safe_edit(text, chat_id, message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_deposit_amount, sent_msg)
        
    elif data == "withdraw":
        text = (f"💸 **Виведення коштів**\n\n"
                f"Курс: **1 ⭐ = {WITHDRAW_RATE_UAH_PER_STAR:.2f} UAH**\n"
                f"Комісія за виведення: **10%**\n\n"
                f"Введіть суму виведення в **⭐**. Мінімальна сума: **{MIN_WITHDRAW_AMOUNT} ⭐**.\n"
                f"Ваш баланс: **{users.get(user_id, {}).get('balance', 0):.2f} ⭐**")
        sent_msg = safe_edit(text, chat_id, message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_withdraw_amount, sent_msg)

    # --- КЕРУВАННЯ БОТОМ ---
    elif data == "check_subscription":
        if is_subscribed(user_id):
            safe_edit("✅ Вітаємо! Ви успішно підписалися на всі канали. Тепер ви можете користуватися ботом.", chat_id, message_id, reply_markup=get_main_reply_markup())
            show_main_menu(user_id, chat_id, message_id)
        else:
            safe_edit("❗️ **Ви не підписалися на всі канали.**\n\n"
                      "Будь ласка, натисніть на посилання вище, щоб підписатися, а потім натисніть '✅ Я підписався'.", chat_id, message_id, reply_markup=get_subscription_markup(), parse_mode="Markdown")

    elif data == "cancel":
        bot.delete_message(chat_id, message_id)
        show_main_menu(user_id, chat_id)
        
    # --- АДМІН-ПАНЕЛЬ ---
    elif str(user_id) == str(ADMIN_ID):
        if data == "admin_panel":
            show_admin_panel(user_id, chat_id, message_id)
            
        elif data == "admin_deposit_requests_list":
            show_deposit_requests_list(chat_id, message_id)

        elif data == "admin_withdraw_requests_list":
            show_withdraw_requests_list(chat_id, message_id)

        elif data.startswith("admin_show_users_"):
            page = int(data.split('_')[3])
            show_users_list(chat_id, message_id, page)
        
        elif data == "admin_market_manage":
            show_admin_market_manage(chat_id, message_id)
        
        elif data == "admin_market_toggle":
            is_open = market_data.get('is_open', True)
            market_data['is_open'] = not is_open
            save_data()
            show_admin_market_manage(chat_id, message_id)
        
        elif data == "admin_set_market_price":
            text = (f"✏️ **Зміна ринкової ціни SNOW**\n\n"
                    f"Поточна ціна: **{market_data['market_price']:.2f} ⭐**\n\n"
                    f"Введіть нову ціну за 1 SNOW:")
            sent_msg = safe_edit(text, chat_id, message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
            if sent_msg:
                bot.register_next_step_handler(sent_msg, process_admin_set_market_price, sent_msg)
            
        elif data == "admin_add_snow":
            text = (f"➕ **Додати SNOW на ринок**\n\n"
                    f"Поточна кількість: **{market_data['snow_available']:.2f} ❄️**\n\n"
                    f"Введіть кількість SNOW, яку потрібно додати:")
            sent_msg = safe_edit(text, chat_id, message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
            if sent_msg:
                bot.register_next_step_handler(sent_msg, process_admin_add_snow, sent_msg)

        elif data == "admin_manage_balance":
            text = "💰 **Керування балансом користувача**\n\nВведіть @username або ID користувача:"
            sent_msg = safe_edit(text, chat_id, message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
            if sent_msg:
                bot.register_next_step_handler(sent_msg, process_admin_find_user, sent_msg)
        
        elif data.startswith("admin_view_deposit_"):
            request_id = data.split('_')[3]
            req = pending_requests.get(request_id)
            if not req or req.get('status') != 'pending':
                safe_edit("❌ Запит не знайдено або вже оброблено.", chat_id, message_id)
                show_admin_panel(user_id, chat_id, message_id)
                return
            
            user_info = users.get(req['user_id'], {})
            text = (f"💳 **Запит на поповнення #{request_id}**\n\n"
                    f"Користувач: @{escape_markdown(user_info.get('username', 'N/A'))}\n"
                    f"Сума поповнення: **{req['amount']:.2f} ⭐**\n"
                    f"Сума в UAH: **{req['amount_uah']:.2f} грн**\n"
                    f"Очікуваний платіж на реквізити: `{DEPOSIT_REQUISITES}`\n\n"
                    f"Після отримання платежу натисніть '✅ Підтвердити'.")
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton("✅ Підтвердити", callback_data=f"admin_approve_deposit_{request_id}"),
                       types.InlineKeyboardButton("❌ Відхилити", callback_data=f"admin_decline_deposit_{request_id}"))
            markup.add(types.InlineKeyboardButton("🔙 До списку", callback_data="admin_deposit_requests_list"))
            safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif data.startswith("admin_view_withdraw_"):
            request_id = data.split('_')[3]
            req = pending_requests.get(request_id)
            if not req or req.get('status') != 'pending':
                safe_edit("❌ Запит не знайдено або вже оброблено.", chat_id, message_id)
                show_admin_panel(user_id, chat_id, message_id)
                return
                
            user_info = users.get(req['user_id'], {})
            text = (f"💸 **Запит на виведення #{request_id}**\n\n"
                    f"Користувач: @{escape_markdown(user_info.get('username', 'N/A'))}\n"
                    f"Сума виведення: **{req['amount']:.2f} ⭐**\n"
                    f"Реквізити: `{escape_markdown(req['requisites'])}`\n"
                    f"Сума до виплати: **{req['amount_uah_after_fee']:.2f} грн**\n\n"
                    f"Після виплати коштів натисніть '✅ Підтвердити'.")
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton("✅ Підтвердити", callback_data=f"admin_approve_withdraw_{request_id}"),
                       types.InlineKeyboardButton("❌ Відхилити", callback_data=f"admin_decline_withdraw_{request_id}"))
            markup.add(types.InlineKeyboardButton("🔙 До списку", callback_data="admin_withdraw_requests_list"))
            safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif data.startswith("admin_approve_deposit_"):
            request_id = data.split('_')[3]
            req = pending_requests.get(request_id)
            if req and req['status'] == 'pending':
                req['status'] = 'approved'
                user_id_to_update = req['user_id']
                user_data = users.get(user_id_to_update, {})
                user_data['balance'] += req['amount']
                save_data()
                bot.send_message(user_id_to_update, f"✅ Ваш запит на поповнення на суму **{req['amount']:.2f} ⭐** був успішно схвалений!", parse_mode="Markdown")
                safe_edit(f"✅ Запит #{request_id} на поповнення підтверджено.", chat_id, message_id, reply_markup=get_admin_panel_markup())
            else:
                safe_edit("❌ Помилка: запит не знайдено або вже оброблено.", chat_id, message_id)
                
        elif data.startswith("admin_decline_deposit_"):
            request_id = data.split('_')[3]
            req = pending_requests.get(request_id)
            if req and req['status'] == 'pending':
                req['status'] = 'declined'
                save_data()
                bot.send_message(req['user_id'], f"❌ Ваш запит на поповнення на суму **{req['amount']:.2f} ⭐** був відхилений. Будь ласка, зверніться до адміністратора.", parse_mode="Markdown")
                safe_edit(f"❌ Запит #{request_id} на поповнення відхилено.", chat_id, message_id, reply_markup=get_admin_panel_markup())
            else:
                safe_edit("❌ Помилка: запит не знайдено або вже оброблено.", chat_id, message_id)
                
        elif data.startswith("admin_approve_withdraw_"):
            request_id = data.split('_')[3]
            req = pending_requests.get(request_id)
            if req and req['status'] == 'pending':
                req['status'] = 'approved'
                save_data()
                bot.send_message(req['user_id'], f"✅ Ваш запит на виведення на суму **{req['amount']:.2f} ⭐** був успішно схвалений. Кошти відправлено!", parse_mode="Markdown")
                safe_edit(f"✅ Запит #{request_id} на виведення підтверджено.", chat_id, message_id, reply_markup=get_admin_panel_markup())
            else:
                safe_edit("❌ Помилка: запит не знайдено або вже оброблено.", chat_id, message_id)

        elif data.startswith("admin_decline_withdraw_"):
            request_id = data.split('_')[3]
            req = pending_requests.get(request_id)
            if req and req['status'] == 'pending':
                user_id_to_update = req['user_id']
                user_data = users.get(user_id_to_update, {})
                user_data['balance'] += req['amount']
                req['status'] = 'declined'
                save_data()
                bot.send_message(user_id_to_update, f"❌ Ваш запит на виведення на суму **{req['amount']:.2f} ⭐** був відхилений. Кошти повернуто на баланс. Будь ласка, зверніться до адміністратора.", parse_mode="Markdown")
                safe_edit(f"❌ Запит #{request_id} на виведення відхилено. Кошти повернено користувачу.", chat_id, message_id, reply_markup=get_admin_panel_markup())
            else:
                safe_edit("❌ Помилка: запит не знайдено або вже оброблено.", chat_id, message_id)
        
        # Покроковий процес створення промокоду
        elif data == "admin_create_promo_step1":
            text = "🎁 **Створення промокоду (Крок 1/3)**\n\nВведіть назву промокоду (без пробілів):"
            sent_msg = safe_edit(text, chat_id, message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
            if sent_msg:
                bot.register_next_step_handler(sent_msg, process_create_promo_name, sent_msg)
        
        elif data == "admin_top_referrers":
            referer_counts = {}
            for user_data in users.values():
                referer_id = user_data.get('referer')
                if referer_id:
                    referer_counts[referer_id] = referer_counts.get(referer_id, 0) + 1
            
            top_referrers = sorted(referer_counts.items(), key=lambda item: item[1], reverse=True)[:15]

            if not top_referrers:
                text = "🏆 **Топ 15 реферерів**\n\nНаразі ніхто не запросив друзів."
            else:
                text = "🏆 **Топ 15 реферерів:**\n\n"
                for i, (referer_id, count) in enumerate(top_referrers):
                    referer_data = users.get(referer_id, {})
                    username = escape_markdown(referer_data.get('username', 'N/A'))
                    text += f"**{i+1}.** @{username} - **{count}** рефералів\n"
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Адмін-панель", callback_data="admin_panel"))
            safe_edit(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif data.startswith("admin_delete_review_"):
            try:
                review_index = int(data.split('_')[3]) - 1
                if 0 <= review_index < len(reviews):
                    del reviews[review_index]
                    save_data()
                    safe_edit(f"✅ Відгук #{review_index+1} успішно видалено.", chat_id, message_id)
                    show_reviews(user_id, chat_id, message_id)
                else:
                    safe_edit("❌ Некоректний номер відгуку.", chat_id, message_id)
                    show_reviews(user_id, chat_id, message_id)
            except (ValueError, IndexError):
                safe_edit("❌ Помилка при видаленні відгуку.", chat_id, message_id)
                show_reviews(user_id, chat_id, message_id)

    else: # Загальний обробник для невідомих колбеків, якщо користувач не адмін.
        safe_edit("❌ Невідома дія. Повертаюся до головного меню.", chat_id, message_id)
        show_main_menu(user_id, chat_id)
        return


# --- ОБРОБНИКИ ДЛЯ TEXT ВІД АДМІНА ---
def get_admin_panel_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Адмін-панель", callback_data="admin_panel"))
    return markup

def process_create_promo_name(message, message_to_edit):
    user_id = str(message.from_user.id)
    promo_code = message.text.strip().upper()
    bot.delete_message(message.chat.id, message.message_id)
    
    if promo_code.lower() == "❌ скасувати":
        show_admin_panel(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    if not promo_code.isalnum() or ' ' in promo_code:
        text = "❌ Назва промокоду має містити лише букви та цифри, без пробілів."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_create_promo_name, sent_msg)
        return
    
    if promo_code in promos:
        text = "❌ Промокод з такою назвою вже існує. Використайте іншу назву."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_create_promo_name, sent_msg)
        return

    admin_promo_creation_state[user_id] = {'code': promo_code}
    
    text = f"🎁 **Створення промокоду (Крок 2/3)**\n\nПромокод: **{promo_code}**\nВведіть суму бонусу в **⭐**:"
    sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
    if sent_msg:
        bot.register_next_step_handler(sent_msg, process_create_promo_amount, sent_msg)

def process_create_promo_amount(message, message_to_edit):
    user_id = str(message.from_user.id)
    amount_text = message.text.strip()
    bot.delete_message(message.chat.id, message.message_id)
    
    if amount_text.lower() == "❌ скасувати":
        del admin_promo_creation_state[user_id]
        show_admin_panel(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    bonus_amount = parse_amount(amount_text)
    if bonus_amount is None or bonus_amount <= 0:
        text = "❌ Некоректна сума бонусу. Введіть число більше 0."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_create_promo_amount, sent_msg)
        return

    admin_promo_creation_state[user_id]['bonus'] = bonus_amount
    
    text = (f"🎁 **Створення промокоду (Крок 3/3)**\n\n"
            f"Промокод: **{admin_promo_creation_state[user_id]['code']}**\n"
            f"Бонус: **{bonus_amount:.2f} ⭐**\n\n"
            f"Введіть кількість активацій (наприклад, 100):")
    sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
    if sent_msg:
        bot.register_next_step_handler(sent_msg, process_create_promo_activations, sent_msg)

def process_create_promo_activations(message, message_to_edit):
    user_id = str(message.from_user.id)
    activations_text = message.text.strip()
    bot.delete_message(message.chat.id, message.message_id)
    
    if activations_text.lower() == "❌ скасувати":
        del admin_promo_creation_state[user_id]
        show_admin_panel(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    try:
        max_activations = int(activations_text)
        if max_activations <= 0:
            raise ValueError
    except ValueError:
        text = "❌ Некоректна кількість активацій. Введіть ціле число більше 0."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_create_promo_activations, sent_msg)
        return
        
    promo_data = admin_promo_creation_state.pop(user_id)
    promo_code = promo_data['code']
    bonus_amount = promo_data['bonus']
    
    promos[promo_code] = {
        'bonus': bonus_amount,
        'max_activations': max_activations,
        'used_activations': 0,
        'used_by_users': []
    }
    save_data()
    
    text = (f"✅ Промокод `{promo_code}` успішно створено!\n\n"
            f"Бонус: **{bonus_amount:.2f} ⭐**\n"
            f"Кількість активацій: **{max_activations}**")
    safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_admin_panel_markup(), parse_mode="Markdown")
    
# Обробник активації промокоду для звичайних користувачів
def process_promo_code(message, message_to_edit):
    user_id = str(message.from_user.id)
    promo_code = message.text.strip().upper()
    bot.delete_message(message.chat.id, message.message_id)
    
    if promo_code.lower() == "❌ скасувати":
        show_profile_menu(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    if promo_code not in promos:
        text = "❌ Промокод не знайдено."
        safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        bot.register_next_step_handler(message_to_edit, process_promo_code, message_to_edit)
        return
        
    promo_data = promos[promo_code]
    
    if user_id in promo_data.get('used_by_users', []):
        text = "❌ Ви вже активували цей промокод."
        safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        bot.register_next_step_handler(message_to_edit, process_promo_code, message_to_edit)
        return

    if promo_data.get('used_activations', 0) >= promo_data.get('max_activations', 0):
        text = "❌ Вичерпано ліміт активацій для цього промокоду."
        safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        bot.register_next_step_handler(message_to_edit, process_promo_code, message_to_edit)
        return
        
    # Активація успішна
    bonus = promo_data['bonus']
    users[user_id]['balance'] += bonus
    promo_data['used_activations'] += 1
    promo_data['used_by_users'].append(user_id)
    save_data()
    
    text = f"🎉 Ви успішно активували промокод `{promo_code}` і отримали **{bonus:.2f} ⭐**!"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Профіль", callback_data="profile"))
    safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=markup, parse_mode="Markdown")


def process_review(message, message_to_edit):
    user_id = str(message.from_user.id)
    review_text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    
    if review_text.lower() == "❌ скасувати":
        safe_edit("❌ Створення відгуку скасовано.", message_to_edit.chat.id, message_to_edit.message_id)
        show_profile_menu(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    reviews.append({
        'user_id': user_id,
        'username': users[user_id].get('username', 'N/A'),
        'text': review_text,
        'timestamp': datetime.now().isoformat()
    })
    save_data()
    safe_edit("✅ Ваш відгук успішно додано!", message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_main_reply_markup())
    show_profile_menu(user_id, message_to_edit.chat.id, message_to_edit.message_id)

def process_buy_snow_amount(message, message_to_edit):
    user_id = str(message.from_user.id)
    amount_text = message.text.lower().strip()
    bot.delete_message(message.chat.id, message.message_id)
    
    if amount_text == '❌ скасувати':
        show_investments_menu(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    amount = parse_amount(amount_text)
    if amount is None or amount <= 0:
        text = "❌ Некоректна сума. Введіть число більше 0."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_buy_snow_amount, sent_msg)
        return

    market_price = market_data.get('market_price', 0)
    cost = amount * market_price
    user_balance = users.get(user_id, {}).get('balance', 0)
    snow_available = market_data.get('snow_available', 0)

    if cost > user_balance:
        text = f"❌ У вас недостатньо коштів. Ваш баланс: {user_balance:.2f} ⭐."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_buy_snow_amount, sent_msg)
        return

    if amount > snow_available:
        text = f"❌ Недостатньо SNOW на ринку. Доступно: {snow_available:.2f} ❄️."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_buy_snow_amount, sent_msg)
        return

    users[user_id]['balance'] -= cost
    users[user_id]['snow_balance'] += amount
    market_data['snow_available'] -= amount
    save_data()
    text = f"✅ Ви успішно купили **{amount:.2f} ❄️** за **{cost:.2f} ⭐**."
    safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, parse_mode="Markdown")
    show_investments_menu(user_id, message_to_edit.chat.id, message_to_edit.message_id)

def process_dice_bet(message, message_to_edit, choice):
    user_id = str(message.from_user.id)
    bet_text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    
    if bet_text.lower() == "❌ скасувати":
        safe_edit(f"❌ Дію скасовано.", message_to_edit.chat.id, message_to_edit.message_id)
        show_main_menu(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    bet = parse_amount(bet_text)
    if bet is None or bet < MIN_GAME_BET:
        text = f"❌ Некоректна ставка. Введіть число не менше {MIN_GAME_BET} ⭐."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_dice_bet, sent_msg, choice)
        return

    user_balance = users.get(user_id, {}).get('balance', 0)
    if user_balance < bet:
        text = "❌ У вас недостатньо коштів. Спробуйте іншу суму."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_dice_bet, sent_msg, choice)
        return

    start_dice_game(user_id, bet, message_to_edit, choice)

def start_dice_game(user_id, bet, message_to_edit, choice):
    users[user_id]['balance'] -= bet
    save_data()
    safe_edit("🎲 Кидаємо кубик...", message_to_edit.chat.id, message_to_edit.message_id)
    time.sleep(2)
    dice_roll = random.randint(1, 6)
    is_even = dice_roll % 2 == 0
    player_win = (choice == 'even' and is_even) or (choice == 'odd' and not is_even)
    result_text = (f"🎲 **Гра 'Кістки'**\n\n"
                   f"**Ваша ставка:** {bet:.2f} ⭐\n"
                   f"Ваш вибір: **{'Парне' if choice == 'even' else 'Непарне'}**\n"
                   f"Випало: **{dice_roll}** ({'Парне' if is_even else 'Непарне'})\n\n")
    win_amount = 0
    if player_win:
        win_amount = bet * 2
        users[user_id]['balance'] += win_amount
        result_text += f"🎉 **Ви виграли!** Ви отримуєте **{win_amount:.2f} ⭐**.\n"
    else:
        result_text += f"😞 **Ви програли.**\n"
    save_data()
    result_text += f"Ваш новий баланс: **{users[user_id]['balance']:.2f} ⭐**"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎮 Знову грати", callback_data="game_dice"),
               types.InlineKeyboardButton("🔙 Ігри", callback_data="games"))
    safe_edit(result_text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=markup, parse_mode="Markdown")
    if player_win:
        award_referer_earnings(user_id, win_amount - bet)

def process_miner_bet(message, message_to_edit, mines_count):
    user_id = str(message.from_user.id)
    bet_text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    
    if bet_text.lower() == "❌ скасувати":
        safe_edit(f"❌ Дію скасовано.", message_to_edit.chat.id, message_to_edit.message_id)
        show_main_menu(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    bet = parse_amount(bet_text)
    if bet is None or bet < MIN_GAME_BET:
        text = f"❌ Некоректна ставка. Введіть число не менше {MIN_GAME_BET} ⭐."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_miner_bet, sent_msg, mines_count)
        return
        
    user_balance = users.get(user_id, {}).get('balance', 0)
    if user_balance < bet:
        text = "❌ У вас недостатньо коштів. Спробуйте іншу суму."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_miner_bet, sent_msg, mines_count)
        return

    # Створюємо гру і починаємо
    game = create_miner_game(user_id, bet, mines_count)
    users[user_id]['balance'] -= bet
    save_data()

    game_text = (f"⛏️ **Гра 'Сапер'**\n\n"
                 f"Ставка: **{bet:.2f} ⭐**\n"
                 f"Кількість мін: **{mines_count}**\n\n"
                 f"Оберіть клітинку:")
    
    safe_edit(game_text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_miner_markup(user_id), parse_mode="Markdown")


# Функція для обробки ставки на гру "Літаки"
def process_plane_bet(message, message_to_edit):
    user_id = str(message.from_user.id)
    bet_text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    
    if bet_text.lower() == "❌ скасувати":
        safe_edit(f"❌ Дію скасовано.", message_to_edit.chat.id, message_to_edit.message_id)
        show_main_menu(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return
        
    bet = parse_amount(bet_text)
    if bet is None or bet < MIN_GAME_BET:
        text = f"❌ Некоректна ставка. Введіть число не менше {MIN_GAME_BET} ⭐."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_plane_bet, sent_msg)
        return

    user_balance = users.get(user_id, {}).get('balance', 0)
    if user_balance < bet:
        text = "❌ У вас недостатньо коштів. Спробуйте іншу суму."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_plane_bet, sent_msg)
        return

    # Запускаємо гру
    users[user_id]['balance'] -= bet
    save_data()
    start_plane_game(user_id, bet, message_to_edit)


# Функція для обробки введення суми поповнення
def process_deposit_amount(message, message_to_edit):
    user_id = str(message.from_user.id)
    amount_text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    
    if amount_text.lower() == "❌ скасувати":
        safe_edit(f"❌ Дію скасовано.", message_to_edit.chat.id, message_to_edit.message_id)
        show_profile_menu(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    amount_uah = parse_amount(amount_text)
    if amount_uah is None or amount_uah < MIN_DEPOSIT_AMOUNT:
        text = f"❌ Некоректна сума. Мінімальна сума поповнення: **{MIN_DEPOSIT_AMOUNT} грн**."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_deposit_amount, sent_msg)
        return
        
    amount_stars = amount_uah / DEPOSIT_RATE_UAH_PER_PER_STAR

    request_id = str(uuid.uuid4())
    pending_requests[request_id] = {
        'request_id': request_id,
        'user_id': user_id,
        'username': users[user_id]['username'],
        'type': 'deposit',
        'amount': amount_stars,
        'amount_uah': amount_uah,
        'status': 'pending',
        'timestamp': datetime.now().isoformat()
    }
    save_data()
    
    text = (f"💳 **Запит на поповнення створено!**\n\n"
            f"Сума до сплати: **{amount_uah:.2f} грн**\n"
            f"Ви отримаєте: **{amount_stars:.2f} ⭐**\n\n"
            f"Перекажіть кошти на наступні реквізити та очікуйте підтвердження адміністратором:\n"
            f"`{DEPOSIT_REQUISITES}`\n\n"
            f"Адміністратор: @{(bot.get_chat(ADMIN_ID).username or 'N/A')}\n\n"
            f"Запит буде опрацьовано якнайшвидше.")
            
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Профіль", callback_data="profile"))
    safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=markup, parse_mode="Markdown")


# Функція для обробки введення суми виведення
def process_withdraw_amount(message, message_to_edit):
    user_id = str(message.from_user.id)
    amount_text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    
    if amount_text.lower() == "❌ скасувати":
        safe_edit(f"❌ Дію скасовано.", message_to_edit.chat.id, message_to_edit.message_id)
        show_profile_menu(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    amount_stars = parse_amount(amount_text)
    if amount_stars is None or amount_stars < MIN_WITHDRAW_AMOUNT:
        text = f"❌ Некоректна сума. Мінімальна сума для виведення: **{MIN_WITHDRAW_AMOUNT} ⭐**."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_withdraw_amount, sent_msg)
        return
        
    user_balance = users.get(user_id, {}).get('balance', 0)
    if amount_stars > user_balance:
        text = f"❌ Недостатньо коштів на балансі. Ваш баланс: **{user_balance:.2f} ⭐**."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_withdraw_amount, sent_msg)
        return
        
    users[user_id]['balance'] -= amount_stars
    save_data()

    text = "💸 **Виведення коштів**\n\nВведіть номер картки, на яку ви хочете отримати кошти:"
    sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
    if sent_msg:
        bot.register_next_step_handler(sent_msg, process_withdraw_requisites, sent_msg, amount_stars)


def process_withdraw_requisites(message, message_to_edit, amount_stars):
    user_id = str(message.from_user.id)
    requisites = message.text
    bot.delete_message(message.chat.id, message.message_id)
    
    if requisites.lower() == "❌ скасувати":
        users[user_id]['balance'] += amount_stars # Повертаємо кошти
        save_data()
        safe_edit(f"❌ Дію скасовано. Кошти **{amount_stars:.2f} ⭐** повернено на ваш баланс.", message_to_edit.chat.id, message_to_edit.message_id, parse_mode="Markdown")
        show_profile_menu(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    request_id = str(uuid.uuid4())
    amount_uah = amount_stars * WITHDRAW_RATE_UAH_PER_STAR
    
    pending_requests[request_id] = {
        'request_id': request_id,
        'user_id': user_id,
        'username': users[user_id]['username'],
        'type': 'withdraw',
        'amount': amount_stars,
        'requisites': requisites,
        'amount_uah_after_fee': amount_uah,
        'status': 'pending',
        'timestamp': datetime.now().isoformat()
    }
    save_data()
    
    text = (f"💸 **Запит на виведення створено!**\n\n"
            f"Сума в **⭐**: **{amount_stars:.2f} ⭐**\n"
            f"Сума до виплати: **{amount_uah:.2f} грн**\n"
            f"Реквізити: `{escape_markdown(requisites)}`\n\n"
            f"Очікуйте, поки адміністратор обробить ваш запит.")
            
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Профіль", callback_data="profile"))
    safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=markup, parse_mode="Markdown")


# АДМІН-ФУНКЦІЇ (ОБРОБНИКИ ДЛЯ TEXT)
def process_admin_set_market_price(message, message_to_edit):
    user_id = str(message.from_user.id)
    price_text = message.text.lower().strip()
    bot.delete_message(message.chat.id, message.message_id)

    if price_text == '❌ скасувати':
        show_admin_market_manage(message_to_edit.chat.id, message_to_edit.message_id)
        return
    
    new_price = parse_amount(price_text)
    if new_price is None or new_price <= 0:
        text = "❌ Некоректна ціна. Введіть число більше 0."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_admin_set_market_price, sent_msg)
        return
        
    market_data['market_price'] = new_price
    save_data()
    safe_edit(f"✅ Ринкова ціна SNOW успішно змінена на **{new_price:.2f} ⭐**.", message_to_edit.chat.id, message_to_edit.message_id, parse_mode="Markdown")
    show_admin_market_manage(message_to_edit.chat.id, message_to_edit.message_id)


def process_admin_add_snow(message, message_to_edit):
    user_id = str(message.from_user.id)
    amount_text = message.text.lower().strip()
    bot.delete_message(message.chat.id, message.message_id)
    
    if amount_text == '❌ скасувати':
        show_admin_market_manage(message_to_edit.chat.id, message_to_edit.message_id)
        return

    amount = parse_amount(amount_text)
    if amount is None or amount <= 0:
        text = "❌ Некоректна кількість. Введіть число більше 0."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_admin_add_snow, sent_msg)
        return
        
    market_data['snow_available'] += amount
    save_data()
    safe_edit(f"✅ Успішно додано **{amount:.2f} ❄️** на ринок.", message_to_edit.chat.id, message_to_edit.message_id, parse_mode="Markdown")
    show_admin_market_manage(message_to_edit.chat.id, message_to_edit.message_id)


def process_admin_find_user(message, message_to_edit):
    user_id = str(message.from_user.id)
    query = message.text.lower().strip()
    bot.delete_message(message.chat.id, message.message_id)
    
    if query == '❌ скасувати':
        show_admin_panel(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    found_user_id = find_user_by_id_or_username(query)
    
    if not found_user_id:
        text = "❌ Користувача не знайдено. Спробуйте інший @username або ID."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_admin_find_user, sent_msg)
        return

    user_data = users[found_user_id]
    
    text = (f"👤 **Керування балансом користувача**\n\n"
            f"Користувач: @{escape_markdown(user_data.get('username', 'N/A'))}\n"
            f"ID: `{found_user_id}`\n"
            f"Поточний баланс: **{user_data['balance']:.2f} ⭐**\n\n"
            f"Оберіть дію:")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("➕ Додати ⭐", callback_data=f"admin_add_balance_{found_user_id}"))
    markup.add(types.InlineKeyboardButton("➖ Зняти ⭐", callback_data=f"admin_remove_balance_{found_user_id}"))
    markup.add(types.InlineKeyboardButton("🔙 Адмін-панель", callback_data="admin_panel"))

    safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=markup, parse_mode="Markdown")


# ... (Інші обробники адмін-функцій) ...
def process_admin_add_balance(message, message_to_edit, user_to_update_id):
    user_id = str(message.from_user.id)
    amount_text = message.text.strip()
    bot.delete_message(message.chat.id, message.message_id)

    if amount_text.lower() == "❌ скасувати":
        show_admin_panel(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return

    amount = parse_amount(amount_text)
    if amount is None or amount <= 0:
        text = "❌ Некоректна сума. Введіть число більше 0."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_admin_add_balance, message_to_edit, user_to_update_id)
        return
    
    users[user_to_update_id]['balance'] += amount
    save_data()
    bot.send_message(user_to_update_id, f"➕ Адміністратор додав на ваш баланс **{amount:.2f} ⭐**.")
    safe_edit(f"✅ Баланс користувача оновлено. Новий баланс: **{users[user_to_update_id]['balance']:.2f} ⭐**.", message_to_edit.chat.id, message_to_edit.message_id, parse_mode="Markdown")
    show_admin_panel(user_id, message_to_edit.chat.id, message_to_edit.message_id)


def process_admin_remove_balance(message, message_to_edit, user_to_update_id):
    user_id = str(message.from_user.id)
    amount_text = message.text.strip()
    bot.delete_message(message.chat.id, message.message_id)

    if amount_text.lower() == "❌ скасувати":
        show_admin_panel(user_id, message_to_edit.chat.id, message_to_edit.message_id)
        return
        
    amount = parse_amount(amount_text)
    if amount is None or amount <= 0:
        text = "❌ Некоректна сума. Введіть число більше 0."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_admin_remove_balance, message_to_edit, user_to_update_id)
        return

    if users[user_to_update_id]['balance'] < amount:
        text = f"❌ Недостатньо коштів на балансі користувача. Поточний баланс: **{users[user_to_update_id]['balance']:.2f} ⭐**."
        sent_msg = safe_edit(text, message_to_edit.chat.id, message_to_edit.message_id, reply_markup=get_cancel_inline_markup(), parse_mode="Markdown")
        if sent_msg:
            bot.register_next_step_handler(sent_msg, process_admin_remove_balance, message_to_edit, user_to_update_id)
        return
    
    users[user_to_update_id]['balance'] -= amount
    save_data()
    bot.send_message(user_to_update_id, f"➖ Адміністратор зняв з вашого балансу **{amount:.2f} ⭐**.")
    safe_edit(f"✅ Баланс користувача оновлено. Новий баланс: **{users[user_to_update_id]['balance']:.2f} ⭐**.", message_to_edit.chat.id, message_to_edit.message_id, parse_mode="Markdown")
    show_admin_panel(user_id, message_to_edit.chat.id, message_to_edit.message_id)


# --- ЗАПУСК БОТА ---
if __name__ == '__main__':
    load_data()
    print("Bot is running...")
    bot.polling(non_stop=True)
