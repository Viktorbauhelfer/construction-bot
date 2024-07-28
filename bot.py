import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# Встановлення логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Отримання токену бота та URL для Webhook з змінних середовища
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Ініціалізація функції start
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Додати будову", callback_data='add_building')],
        [InlineKeyboardButton("Редагувати будову", callback_data='edit_building')],
        [InlineKeyboardButton("Додати працівника", callback_data='add_worker')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Оберіть дію:', reply_markup=reply_markup)

# Обробка натискання кнопок
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'add_building':
        query.edit_message_text(text="Введіть назву будови:")
        context.user_data['action'] = 'add_building'
    elif query.data == 'edit_building':
        # Логіка редагування будови
        query.edit_message_text(text="Функція редагування будови ще не реалізована.")
    elif query.data == 'add_worker':
        query.edit_message_text(text="Введіть ім'я працівника:")
        context.user_data['action'] = 'add_worker'

# Обробка текстових повідомлень
def handle_message(update: Update, context: CallbackContext):
    action = context.user_data.get('action')
    if action == 'add_building':
        # Логіка додавання будови
        building_name = update.message.text
        update.message.reply_text(f'Будову "{building_name}" додано.')
        context.user_data['action'] = None
    elif action == 'add_worker':
        # Логіка додавання працівника
        worker_name = update.message.text
        update.message.reply_text(f'Працівника "{worker_name}" додано.')
        context.user_data['action'] = None

# Запуск бота з використанням Webhook
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Встановлення Webhook
    updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=TOKEN
    )
    updater.bot.setWebhook(WEBHOOK_URL + TOKEN)

    updater.idle()

if __name__ == '__main__':
    main()
