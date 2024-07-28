import os
import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Ініціалізація бази даних
conn = sqlite3.connect('construction_bot.db', check_same_thread=False)
cursor = conn.cursor()

# Створення таблиць
cursor.execute('''
CREATE TABLE IF NOT EXISTS workers (
    id INTEGER PRIMARY KEY,
    name TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY,
    address TEXT,
    description TEXT,
    owner TEXT,
    status TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY,
    worker_id INTEGER,
    site_id INTEGER,
    start_time TEXT,
    end_time TEXT
)
''')

conn.commit()

# Функції для команд
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Вітаю! Я будівельний бот. Використовуйте команди для взаємодії зі мною.\n\n'
                              '/add_worker <імʼя> - Додати робітника\n'
                              '/list_workers - Переглянути список робітників\n'
                              '/add_site <адреса>, <опис>, <власник> - Додати будову\n'
                              '/list_sites - Переглянути список будов\n'
                              '/assign <worker_id> <site_id> - Призначити робітника на будову\n'
                              '/checkin <worker_id> - Відмітити прихід\n'
                              '/checkout <worker_id> - Відмітити вихід\n'
                              '/report <site_id> - Звіт по будові\n'
                              '/finish_site <site_id> - Закрити будову\n'
                              '/resume_site <site_id> - Відновити будову\n')

def add_worker(update: Update, context: CallbackContext) -> None:
    name = ' '.join(context.args)
    cursor.execute('INSERT INTO workers (name) VALUES (?)', (name,))
    conn.commit()
    update.message.reply_text(f'Робітник {name} доданий.')

def list_workers(update: Update, context: CallbackContext) -> None:
    cursor.execute('SELECT * FROM workers')
    workers = cursor.fetchall()
    response = '\n'.join([f'{worker[0]}: {worker[1]}' for worker in workers])
    update.message.reply_text(response)

def add_site(update: Update, context: CallbackContext) -> None:
    args = ' '.join(context.args).split(',')
    if len(args) != 3:
        update.message.reply_text('Невірний формат. Використовуйте: /add_site <адреса>, <опис>, <власник>')
        return
    address, description, owner = args
    cursor.execute('INSERT INTO sites (address, description, owner, status) VALUES (?, ?, ?, ?)',
                   (address.strip(), description.strip(), owner.strip(), 'active'))
    conn.commit()
    update.message.reply_text(f'Будова за адресою {address} додана.')

def list_sites(update: Update, context: CallbackContext) -> None:
    cursor.execute('SELECT * FROM sites')
    sites = cursor.fetchall()
    response = '\n'.join([f'{site[0]}: {site[1]} ({site[3]})' for site in sites])
    update.message.reply_text(response)

def assign(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 2:
        update.message.reply_text('Невірний формат. Використовуйте: /assign <worker_id> <site_id>')
        return
    worker_id, site_id = context.args
    cursor.execute('INSERT INTO assignments (worker_id, site_id, start_time) VALUES (?, ?, ?)',
                   (worker_id, site_id, datetime.now().isoformat()))
    conn.commit()
    update.message.reply_text(f'Робітник {worker_id} призначений на будову {site_id}.')

def checkin(update: Update, context: CallbackContext) -> None:
    worker_id = ' '.join(context.args)
    cursor.execute('UPDATE assignments SET start_time = ? WHERE worker_id = ? AND end_time IS NULL',
                   (datetime.now().isoformat(), worker_id))
    conn.commit()
    update.message.reply_text(f'Робітник {worker_id} відмітив прихід.')

def checkout(update: Update, context: CallbackContext) -> None:
    worker_id = ' '.join(context.args)
    cursor.execute('UPDATE assignments SET end_time = ? WHERE worker_id = ? AND end_time IS NULL',
                   (datetime.now().isoformat(), worker_id))
    conn.commit()
    update.message.reply_text(f'Робітник {worker_id} відмітив вихід.')

def report(update: Update, context: CallbackContext) -> None:
    site_id = ' '.join(context.args)
    cursor.execute('SELECT * FROM assignments WHERE site_id = ?', (site_id,))
    assignments = cursor.fetchall()
    response = f'Звіт по будові {site_id}:\n'
    for assignment in assignments:
        worker_id, start_time, end_time = assignment[1], assignment[3], assignment[4]
        response += f'Робітник {worker_id}: Початок - {start_time}, Кінець - {end_time}\n'
    update.message.reply_text(response)

def finish_site(update: Update, context: CallbackContext) -> None:
    site_id = ' '.join(context.args)
    cursor.execute('UPDATE sites SET status = ? WHERE id = ?', ('finished', site_id))
    conn.commit()
    update.message.reply_text(f'Будову {site_id} закрито.')

def resume_site(update: Update, context: CallbackContext) -> None:
    site_id = ' '.join(context.args)
    cursor.execute('UPDATE sites SET status = ? WHERE id = ?', ('active', site_id))
    conn.commit()
    update.message.reply_text(f'Будову {site_id} відновлено.')

def main() -> None:
    token = os.getenv('TELEGRAM_TOKEN')
    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('add_worker', add_worker))
    dispatcher.add_handler(CommandHandler('list_workers', list_workers))
    dispatcher.add_handler(CommandHandler('add_site', add_site))
    dispatcher.add_handler(CommandHandler('list_sites', list_sites))
    dispatcher.add_handler(CommandHandler('assign', assign))
    dispatcher.add_handler(CommandHandler('checkin', checkin))
    dispatcher.add_handler(CommandHandler('checkout', checkout))
    dispatcher.add_handler(CommandHandler('report', report))
    dispatcher.add_handler(CommandHandler('finish_site', finish_site))
    dispatcher.add_handler(CommandHandler('resume_site', resume_site))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
