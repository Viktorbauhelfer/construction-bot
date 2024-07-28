import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import datetime

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define states
ADDRESS, DESCRIPTION, OWNER, WORKER_NICK, WORKER_ACTION = range(5)

# In-memory storage for workers and work logs
workers = {}
work_logs = {}

def start(update: Update, context: CallbackContext) -> int:
    logger.info("Command /start received")
    reply_keyboard = [['Додати будову', 'Додати робітника']]
    update.message.reply_text(
        'Привіт! Я бот для управління будовами. Оберіть дію:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ADDRESS

# (Інші функції бота з аналогічним логуванням)

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
