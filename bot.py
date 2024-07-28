import os
import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Get the Telegram bot token from the environment variable
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Check if the TOKEN is correctly fetched
if not TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found in environment variables")

# Define states
MAIN_MENU, ADD_SITE, ADDRESS, DESCRIPTION, OWNER, WORKER_NICK, WORKER_ACTION, EDIT_SITE = range(8)

# In-memory storage for sites, workers, and work logs
sites = {}
workers = {}
work_logs = {}

def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Додати будову', 'Додати робітника', 'Редагувати будову', 'Зареєструвати дію']]
    update.message.reply_text(
        'Привіт! Я бот для управління будовами. Оберіть дію:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MAIN_MENU

def main_menu(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text
    if user_choice == 'Додати будову':
        update.message.reply_text('Введіть адресу будови:', reply_markup=ReplyKeyboardRemove())
        return ADDRESS
    elif user_choice == 'Додати робітника':
        update.message.reply_text('Введіть нік робітника в Telegram:', reply_markup=ReplyKeyboardRemove())
        return WORKER_NICK
    elif user_choice == 'Редагувати будову':
        if not sites:
            update.message.reply_text('Немає доступних будов для редагування.')
            return MAIN_MENU
        site_list = [[address] for address in sites.keys()]
        update.message.reply_text(
            'Оберіть будову для редагування:',
            reply_markup=ReplyKeyboardMarkup(site_list, one_time_keyboard=True)
        )
        return EDIT_SITE
    elif user_choice == 'Зареєструвати дію':
        update.message.reply_text('Введіть нік робітника в Telegram:', reply_markup=ReplyKeyboardRemove())
        return WORKER_ACTION
    else:
        update.message.reply_text('Будь ласка, оберіть дію з меню.')
        return MAIN_MENU

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
    address = user_data['address']
    sites[address] = {
        'description': user_data['description'],
        'owner': update.message.text
    }
    update.message.reply_text(
        f"Будову за адресою {address} успішно додано!\n"
        f"Опис: {sites[address]['description']}\n"
        f"Власник: {sites[address]['owner']}"
    )
    return MAIN_MENU

def add_worker(update: Update, context: CallbackContext) -> int:
    worker_nick = update.message.text
    workers[worker_nick] = {'status': 'active'}
    update.message.reply_text(f"Робітника @{worker_nick} додано успішно!")
    return MAIN_MENU

def log_work(update: Update, context: CallbackContext) -> int:
    user_nick = update.message.text
    if user_nick not in workers:
        update.message.reply_text('Ви не зареєстровані як робітник.')
        return MAIN_MENU
    reply_keyboard = [['Прийшов', 'Пішов']]
    update.message.reply_text(
        'Оберіть дію:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    context.user_data['worker_nick'] = user_nick
    return WORKER_ACTION

def worker_action(update: Update, context: CallbackContext) -> int:
    user_nick = context.user_data['worker_nick']
    action = update.message.text
    if user_nick not in work_logs:
        work_logs[user_nick] = []
    work_logs[user_nick].append({'action': action, 'time': datetime.datetime.now()})
    update.message.reply_text(f"Дія '{action}' зареєстрована для @{user_nick}")
    return MAIN_MENU

def edit_site(update: Update, context: CallbackContext) -> int:
    address = update.message.text
    context.user_data['edit_address'] = address
    reply_keyboard = [['Редагувати опис', 'Видалити будову']]
    update.message.reply_text(
        f"Оберіть дію для будови за адресою {address}:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return EDIT_SITE

def edit_site_choice(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text
    address = context.user_data['edit_address']
    if user_choice == 'Редагувати опис':
        update.message.reply_text('Введіть новий опис будови:')
        return DESCRIPTION
    elif user_choice == 'Видалити будову':
        del sites[address]
        update.message.reply_text(f"Будову за адресою {address} успішно видалено.")
        return MAIN_MENU
    else:
        update.message.reply_text('Будь ласка, оберіть дію з меню.')
        return EDIT_SITE

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [MessageHandler(Filters.text & ~Filters.command, main_menu)],
            ADD_SITE: [MessageHandler(Filters.text & ~Filters.command, add_site)],
            ADDRESS: [MessageHandler(Filters.text & ~Filters.command, address)],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, description)],
            OWNER: [MessageHandler(Filters.text & ~Filters.command, owner)],
            WORKER_NICK: [MessageHandler(Filters.text & ~Filters.command, add_worker)],
            WORKER_ACTION: [MessageHandler(Filters.text & ~Filters.command, worker_action)],
            EDIT_SITE: [MessageHandler(Filters.text & ~Filters.command, edit_site)],
            EDIT_SITE_CHOICE: [MessageHandler(Filters.text & ~Filters.command, edit_site_choice)],
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
