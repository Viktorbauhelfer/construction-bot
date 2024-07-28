import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Get the Telegram bot token from the environment variable
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Check if the TOKEN is correctly fetched
if not TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found in environment variables")

# Define states
ADDRESS, DESCRIPTION, OWNER, WORKER_NICK, WORKER_ACTION = range(5)

# In-memory storage for workers and work logs
workers = {}
work_logs = {}

def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Додати будову', 'Додати робітника']]
    update.message.reply_text(
        'Привіт! Я бот для управління будовами. Оберіть дію:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ADDRESS

def add_site(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Введіть адресу будови:',
        reply_markup=ReplyKeyboardRemove()
    )
    return ADDRESS

def address(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['address'] = update.message.text
    update.message.reply_text('Введіть опис будови:')
    return DESCRIPTION

def description(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['description'] = update.message.text
    update.message.reply_text('Введіть ім\'я власника будови:')
    return OWNER

def owner(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['owner'] = update.message.text
    update.message.reply_text(
        f"Адреса: {user_data['address']}\n"
        f"Опис: {user_data['description']}\n"
        f"Власник: {user_data['owner']}\n"
        f"Будову додано успішно!"
    )
    return ConversationHandler.END

def add_worker(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Введіть нік робітника в Telegram:')
    return WORKER_NICK

def worker_nick(update: Update, context: CallbackContext) -> int:
    worker_nick = update.message.text
    workers[worker_nick] = {'status': 'active'}
    update.message.reply_text(f"Робітника @{worker_nick} додано успішно!")
    return ConversationHandler.END

def log_work(update: Update, context: CallbackContext) -> int:
    user_nick = update.message.from_user.username
    if user_nick not in workers:
        update.message.reply_text('Ви не зареєстровані як робітник.')
        return ConversationHandler.END
    reply_keyboard = [['Прийшов', 'Пішов']]
    update.message.reply_text(
        'Оберіть дію:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return WORKER_ACTION

def worker_action(update: Update, context: CallbackContext) -> int:
    user_nick = update.message.from_user.username
    action = update.message.text
    if user_nick not in work_logs:
        work_logs[user_nick] = []
    work_logs[user_nick].append({'action': action, 'time': datetime.datetime.now()})
    update.message.reply_text(f"Дія '{action}' зареєстрована для @{user_nick}")
    return ConversationHandler.END

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states ADDRESS, DESCRIPTION, OWNER, WORKER_NICK, WORKER_ACTION
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ADDRESS: [MessageHandler(Filters.text & ~Filters.command, address)],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, description)],
            OWNER: [MessageHandler(Filters.text & ~Filters.command, owner)],
            WORKER_NICK: [MessageHandler(Filters.text & ~Filters.command, worker_nick)],
            WORKER_ACTION: [MessageHandler(Filters.text & ~Filters.command, worker_action)]
        },
        fallbacks=[CommandHandler('start', start)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
