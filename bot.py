import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext
from dotenv import load_dotenv

# Завантаження токену з .env файлу
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Стан для ConversationHandler
CHOOSING, TYPING_NAME, TYPING_ADDRESS, TYPING_OWNER, ADDING_WORKER, WORKER_HOURS = range(6)

# Словник для зберігання даних
construction_data = {}
worker_data = {}

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Додати будову", callback_data='add_construction')],
        [InlineKeyboardButton("Додати робітника", callback_data='add_worker')],
        [InlineKeyboardButton("Ввести робочі години", callback_data='add_hours')],
        [InlineKeyboardButton("Повернутись в головне меню", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Привіт! Я бот для управління будовами. Оберіть дію:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'add_construction':
        query.edit_message_text(text="Введіть назву будови:")
        return TYPING_NAME
    elif query.data == 'add_worker':
        query.edit_message_text(text="Введіть Telegram username робітника:")
        return ADDING_WORKER
    elif query.data == 'add_hours':
        query.edit_message_text(text="Введіть будову, на якій ви працюєте:")
        return WORKER_HOURS
    elif query.data == 'main_menu':
        start(update, context)
        return ConversationHandler.END

def construction_name(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    user_data['construction_name'] = update.message.text
    update.message.reply_text('Введіть адресу будови:')
    return TYPING_ADDRESS

def construction_address(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    user_data['construction_address'] = update.message.text
    update.message.reply_text('Введіть ім\'я власника будови:')
    return TYPING_OWNER

def construction_owner(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    user_data['construction_owner'] = update.message.text

    construction_name = user_data['construction_name']
    construction_address = user_data['construction_address']
    construction_owner = user_data['construction_owner']

    construction_data[construction_name] = {
        'address': construction_address,
        'owner': construction_owner
    }

    update.message.reply_text(f"Будову '{construction_name}' додано з адресою '{construction_address}' та власником '{construction_owner}'.")
    start(update, context)
    return ConversationHandler.END

def add_worker(update: Update, context: CallbackContext) -> None:
    username = update.message.text
    worker_data[username] = {'constructions': []}
    update.message.reply_text(f"Робітника '{username}' додано.")
    start(update, context)
    return ConversationHandler.END

def worker_hours_construction(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    construction_name = update.message.text

    if construction_name in construction_data:
        if username in worker_data:
            worker_data[username]['current_construction'] = construction_name
            update.message.reply_text(f"Введіть дату (у форматі YYYY-MM-DD) та години (з-до) роботи для '{construction_name}':")
            return WORKER_HOURS
        else:
            update.message.reply_text("Ви не є зареєстрованим робітником.")
            start(update, context)
            return ConversationHandler.END
    else:
        update.message.reply_text("Будову не знайдено. Спробуйте ще раз.")
        return WORKER_HOURS

def worker_hours(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    construction_name = worker_data[username]['current_construction']
    hours = update.message.text

    if 'hours' not in worker_data[username]:
        worker_data[username]['hours'] = {}
    
    if construction_name not in worker_data[username]['hours']:
        worker_data[username]['hours'][construction_name] = []

    worker_data[username]['hours'][construction_name].append(hours)
    update.message.reply_text(f"Години роботи для '{construction_name}' додано.")
    start(update, context)
    return ConversationHandler.END

def main() -> None:
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [CallbackQueryHandler(button)],
            TYPING_NAME: [MessageHandler(Filters.text & ~Filters.command, construction_name)],
            TYPING_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, construction_address)],
            TYPING_OWNER: [MessageHandler(Filters.text & ~Filters.command, construction_owner)],
            ADDING_WORKER: [MessageHandler(Filters.text & ~Filters.command, add_worker)],
            WORKER_HOURS: [MessageHandler(Filters.text & ~Filters.command, worker_hours)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
