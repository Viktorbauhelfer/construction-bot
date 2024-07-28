import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Отримання токену бота з оточення
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    logger.error("BOT_TOKEN is not set in the environment variables")
    raise ValueError("BOT_TOKEN is not set in the environment variables")

# Дані для збереження будівель та робітників
buildings = {}
workers = {}
work_hours = {}

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Додати будову", callback_data='add_building')],
        [InlineKeyboardButton("Додати робітника", callback_data='add_worker')],
        [InlineKeyboardButton("Закріпити робітника за будовою", callback_data='assign_worker')],
        [InlineKeyboardButton("Архів будов", callback_data='archive_buildings')],
        [InlineKeyboardButton("Архів робітників", callback_data='archive_workers')],
        [InlineKeyboardButton("Відслідкування годин", callback_data='track_hours')],
        [InlineKeyboardButton("Повернутись до меню", callback_data='start')]
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

    if data == 'start':
        start(update, context)
    elif data == 'add_building':
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
        query.edit_message_text(text=f"Будова '{building_name}':", reply_markup=reply_markup)
    elif data.startswith('assign_'):
        parts = data.split('_')
        building_name = parts[1]
        worker_name = parts[2]
        buildings[building_name]['workers'].append(worker_name)
        workers[worker_name]['buildings'].append(building_name)
        update.callback_query.message.reply_text(f"Робітника '{worker_name}' закріплено за будовою '{building_name}'.")
        context.user_data['action'] = None
        return_to_menu(update, context)
    elif data.startswith('track_hours_'):
        building_name = data.split('_')[2]
        keyboard = [[InlineKeyboardButton(worker, callback_data=f'track_worker_hours_{building_name}_{worker}') for worker in buildings[building_name]['workers']]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"Виберіть робітника для відслідкування годин у будові '{building_name}':", reply_markup=reply_markup)
    elifпродовження:

```python
    data.startswith('track_worker_hours_'):
        parts = data.split('_')
        building_name = parts[3]
        worker_name = parts[4]
        context.user_data['current_building'] = building_name
        context.user_data['current_worker'] = worker_name
        query.edit_message_text(text=f"Введіть кількість годин для робітника '{worker_name}' у будові '{building_name}':")
        context.user_data['action'] = 'track_hours_entry'
    elif data.startswith('edit_address_'):
        building_name = data.split('_')[2]
        context.user_data['current_building'] = building_name
        query.edit_message_text(text=f"Введіть нову адресу для будови '{building_name}':")
        context.user_data['action'] = 'edit_address'
    elif data.startswith('delete_building_'):
        building_name = data.split('_')[2]
        if building_name in buildings:
            del buildings[building_name]
            query.edit_message_text(text=f"Будову '{building_name}' видалено.")
        else:
            query.edit_message_text(text=f"Будову '{building_name}' не знайдено.")
        return_to_menu(update, context)
    elif data.startswith('edit_worker_'):
        worker_name = data.split('_')[2]
        keyboard = [
            [InlineKeyboardButton("Видалити робітника", callback_data=f'delete_worker_{worker_name}')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"Робітник '{worker_name}':", reply_markup=reply_markup)
    elif data.startswith('delete_worker_'):
        worker_name = data.split('_')[2]
        if worker_name in workers:
            del workers[worker_name]
            query.edit_message_text(text=f"Робітника '{worker_name}' видалено.")
        else:
            query.edit_message_text(text=f"Робітника '{worker_name}' не знайдено.")
        return_to_menu(update, context)

# Обробка тексту для відслідковування годин
def handle_hours_entry(update: Update, context: CallbackContext) -> None:
    user_action = context.user_data.get('action')
    if user_action == 'track_hours_entry':
        try:
            hours = float(update.message.text)
            building_name = context.user_data.get('current_building')
            worker_name = context.user_data.get('current_worker')
            if building_name and worker_name:
                if building_name not in work_hours:
                    work_hours[building_name] = {}
                if worker_name not in work_hours[building_name]:
                    work_hours[building_name][worker_name] = []
                work_hours[building_name][worker_name].append(hours)
                update.message.reply_text(f"Додано {hours} годин для робітника '{worker_name}' у будові '{building_name}'.")
                context.user_data['action'] = None
                context.user_data['current_building'] = None
                context.user_data['current_worker'] = None
                return_to_menu(update, context)
        except ValueError:
            update.message.reply_text("Будь ласка, введіть коректне число годин.")

# Запуск бота
def main() -> None:
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_hours_entry))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
