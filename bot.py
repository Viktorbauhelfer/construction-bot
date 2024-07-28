import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Отримання токену бота з оточення
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Дані для збереження будівель та робітників
buildings = {}
workers = {}
work_hours = {}

# Стартова команда
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Додати будову", callback_data='add_building')],
        [InlineKeyboardButton("Додати робітника", callback_data='add_worker')],
        [InlineKeyboardButton("Закріпити робітника за будовою", callback_data='assign_worker')],
        [InlineKeyboardButton("Архів будов", callback_data='archive_buildings')],
        [InlineKeyboardButton("Архів робітників", callback_data='archive_workers')],
        [InlineKeyboardButton("Відслідкування годин", callback_data='track_hours')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Ласкаво просимо! Виберіть опцію:', reply_markup=reply_markup)

# Повернення до меню
def return_to_menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Повернутись до меню", callback_data='start')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Виберіть опцію:', reply_markup=reply_markup)

# Додавання будови
def add_building(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    context.user_data['action'] = 'add_building'
    query.edit_message_text(text="Введіть назву будови:")

# Додавання робітника
def add_worker(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    context.user_data['action'] = 'add_worker'
    query.edit_message_text(text="Введіть ім'я робітника:")

# Закріплення робітника за будовою
def assign_worker(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    context.user_data['action'] = 'assign_worker'
    query.edit_message_text(text="Введіть ім'я робітника для закріплення:")

# Обробка текстових повідомлень
def handle_text(update: Update, context: CallbackContext) -> None:
    user_action = context.user_data.get('action')
    if user_action == 'add_building':
        building_name = update.message.text
        buildings[building_name] = {'address': None, 'workers': []}
        context.user_data['current_building'] = building_name
        update.message.reply_text(f"Будову '{building_name}' додано. Введіть адресу будови:")
        context.user_data['action'] = 'add_address'
    elif user_action == 'add_address':
        address = update.message.text
        current_building = context.user_data.get('current_building')
        if current_building:
            buildings[current_building]['address'] = address
            update.message.reply_text(f"Адресу '{address}' додано до будови '{current_building}'.")
            context.user_data['action'] = None
            context.user_data['current_building'] = None
            return_to_menu(update, context)
    elif user_action == 'add_worker':
        worker_name = update.message.text
        workers[worker_name] = {'buildings': [], 'work_hours': {}}
        update.message.reply_text(f"Робітника '{worker_name}' додано.")
        context.user_data['action'] = None
        return_to_menu(update, context)
    elif user_action == 'assign_worker':
        worker_name = update.message.text
        if worker_name in workers:
            context.user_data['current_worker'] = worker_name
            keyboard = [[InlineKeyboardButton(name, callback_data=f'assign_{name}_{worker_name}') for name in buildings.keys()]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"Виберіть будову для робітника '{worker_name}':", reply_markup=reply_markup)
        else:
            update.message.reply_text(f"Робітника '{worker_name}' не знайдено.")
            context.user_data['action'] = None
            return_to_menu(update, context)

# Архів будов
def archive_buildings(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if buildings:
        keyboard = [[InlineKeyboardButton(name, callback_data=f'edit_building_{name}') for name in buildings.keys()]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Виберіть будову для редагування або видалення:", reply_markup=reply_markup)
    else:
        query.edit_message_text(text="Архів будов порожній.")
    return_to_menu(update, context)

# Архів робітників
def archive_workers(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if workers:
        keyboard = [[InlineKeyboardButton(name, callback_data=f'edit_worker_{name}') for name in workers.keys()]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Виберіть робітника для редагування або видалення:", reply_markup=reply_markup)
    else:
        query.edit_message_text(text="Архів робітників порожній.")
    return_to_menu(update, context)

# Відслідкування годин
def track_hours(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if buildings:
        keyboard = [[InlineKeyboardButton(name, callback_data=f'track_hours_{name}') for name in buildings.keys()]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Виберіть будову для відслідкування годин:", reply_markup=reply_markup)
    else:
        query.edit_message_text(text="Немає будов для відслідкування годин.")
    return_to_menu(update, context)

# Обробка callback запитів
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    data = query.data

    if data == 'add_building':
        add_building(update, context)
    elif data == 'add_worker':
        add_worker(update, context)
    elif data == 'assign_worker':
        assign_worker(update, context)
    elif data == 'archive_buildings':
        archive_buildings(update, context)
    elif data == 'archive_workers':
        archive_workers(update, context)
    elif data == 'track_hours':
        track_hours(update, context)
    elif data.startswith('edit_building_'):
        building_name = data.split('_')[2]
        keyboard = [
            [InlineKeyboardButton("Редагувати адресу", callback_data=f'edit_address_{building_name}')],
            [InlineKeyboardButton("Видалити будову", callback_data=f'delete_building_{building_name}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"Виберіть дію для будови '{building_name}':", reply_markup=reply_markup)
    elif data.startswith('edit_address_'):
        building_name = data.split('_')[2]
        context.user_data['action'] = 'edit_address'
        context.user_data['current_building'] = building_name
        query.edit_message_text(text=f"Введіть нову адресу для будови '{building_name}':")
    elif data.startswith('delete_building_'):
        building_name = data.split('_')[2]
        buildings.pop(building_name, None)
        query.edit_message_text(text=f"Будову '{building_name}' видалено.")
    elif data.startswith('edit_worker_'):
        worker_name = data.split('_')[2]
        keyboard = [
            [InlineKeyboardButton("Видалити робітника", callback_data=f'delete_worker_{worker_name}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"Виберіть дію для робітника '{worker_name}':", reply_markup=reply_markup)
    elif data.startswith('delete_worker_'):
        worker_name = data.split('_')[2]
        workers.pop(worker_name, None)
        query.edit_message_text(text=f"Робітника '{worker_name}' видалено.")
    elif data.startswith('track
