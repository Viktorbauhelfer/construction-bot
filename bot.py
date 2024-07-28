import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Встановлення логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelень)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Отримання токену бота та URL для Webhook з змінних середовища
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Ініціалізація функції start
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Додати будову", callback_data='add_building')],
        [InlineKeyboardButton("Редагувати будову", callback_data='edit_building')],
        [InlineKeyboardButton("Додати працівника", callback_data='add_worker')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Оберіть дію:', reply_markup=reply_markup)

# Обробка натискання кнопок
async def button(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'add_building':
        await query.edit_message_text(text="Введіть назву будови:")
        context.user_data['action'] = 'add_building'
    elif query.data == 'edit_building':
        # Логіка редагування будови
        await query.edit_message_text(text="Функція редагування будови ще не реалізована.")
    elif query.data == 'add_worker':
        await query.edit_message_text(text="Введіть ім'я працівника:")
        context.user_data['action'] = 'add_worker'

# Обробка текстових повідомлень
async def handle_message(update: Update, context):
    action = context.user_data.get('action')
    if action == 'add_building':
        # Логіка додавання будови
        building_name = update.message.text
        await update.message.reply_text(f'Будову "{building_name}" додано.')
        context.user_data['action'] = None
    elif action == 'add_worker':
        # Логіка додавання працівника
        worker_name = update.message.text
        await update.message.reply_text(f'Працівника "{worker_name}" додано.')
        context.user_data['action'] = None

# Запуск бота з використанням Webhook
async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Встановлення Webhook
    await application.bot.setWebhook(WEBHOOK_URL + TOKEN)

    # Запуск вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL + TOKEN
    )

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
