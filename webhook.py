import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from telegram.ext import Dispatcher
from flask import Flask, request
from dotenv import load_dotenv

# Завантаження токену з файлу .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

# Тимчасові сховища даних
constructions = {}
workers = {}
construction_workers = {}
worker_hours = {}

# Обробник команди /start
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Додати будову", callback_data='add_construction')],
        [InlineKeyboardButton("Додати робітника", callback_data='add_worker')],
        [InlineKeyboardButton("Закріпити робітника за будовою", callback_data='assign_worker')],
        [InlineKeyboardButton("Відслідковувати години", callback_data='track_hours')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Привіт! Я бот для управління будовами. Оберіть дію:', reply_markup=reply_markup)

# Обробник кнопок
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == 'add_construction':
        query.edit_message_text(text="Введіть назву будови:")
        context.user_data['action'] = 'add_construction'
    elif query.data == 'add_worker':
        query.edit_message_text(text="Введіть ім'я робітника:")
        context.user_data['action'] = 'add_worker'
    elif query.data == 'assign_worker':
        query.edit_message_text(text="Введіть ім'я робітника та будову (через кому):")
        context.user_data['action'] = 'assign_worker'
    elif query.data == 'track_hours':
        query.edit_message_text(text="Введіть будову для відслідковування годин:")
        context.user_data['action'] = 'track_hours'
    elif query.data == 'main_menu':
        start(update, context)

# Обробник повідомлень
def message_handler(update: Update, context: CallbackContext):
    action = context.user_data.get('action')
    
    if action == 'add_construction':
        constructions[update.message.text] = []
        update.message.reply_text(f"Будову '{update.message.text}' додано успішно!")
    elif action == 'add_worker':
        workers[update.message.text] = {'name': update.message.text, 'constructions': []}
        update.message.reply_text(f"Робітника '{update.message.text}' додано успішно!")
    elif action == 'assign_worker':
        worker_name, construction_name = map(str.strip, update.message.text.split(','))
        if worker_name in workers and construction_name in constructions:
            constructions[construction_name].append(worker_name)
            workers[worker_name]['constructions'].append(construction_name)
            update.message.reply_text(f"Робітника '{worker_name}' закріплено за будовою '{construction_name}' успішно!")
        else:
            update.message.reply_text("Робітника або будову не знайдено.")
    elif action == 'track_hours':
        construction_name = update.message.text
        if construction_name in constructions:
            report = f"Години для будови '{construction_name}':\n"
            for worker in constructions[construction_name]:
                hours = worker_hours.get(worker, {}).get(construction_name, 0)
                report += f"{worker}: {hours} годин\n"
            update.message.reply_text(report)
        else:
            update.message.reply_text("Будову не знайдено.")
    
    # Повернення до головного меню
    keyboard = [[InlineKeyboardButton("Повернутися до меню", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Виберіть дію:", reply_markup=reply_markup)

# Основна функція для Webhook
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    
    updater.start_webhook(listen="0.0.0.0",
                          port=int(os.envi
