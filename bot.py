from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import datetime

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
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if user_nick not in work_logs:
        work_logs[user_nick] = []

    if action == 'Прийшов':
        work_logs[user_nick].append({'start': current_time, 'end': None})
        update.message.reply_text(f'Час приходу зареєстровано: {current_time}')
    elif action == 'Пішов':
        if work_logs[user_nick] and work_logs[user_nick][-1]['end'] is None:
            work_logs[user_nick][-1]['end'] = current_time
            update.message.reply_text(f'Час відходу зареєстровано: {current_time}')
        else:
            update.message.reply_text('Спочатку зареєструйте час приходу.')
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Операцію скасовано.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ADDRESS: [MessageHandler(Filters.regex('^(Додати будову)$'), add_site),
                      MessageHandler(Filters.regex('^(Додати робітника)$'), add_worker),
                      MessageHandler(Filters.text & ~Filters.command, address)],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, description)],
            OWNER: [MessageHandler(Filters.text & ~Filters.command, owner)],
            WORKER_NICK: [MessageHandler(Filters.text & ~Filters.command, worker_nick)],
            WORKER_ACTION: [MessageHandler(Filters.text & ~Filters.command, worker_action)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('log_work', log_work))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
