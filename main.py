"""
itsm.mos.ru_4me_parser_bot — минимальная стабильная версия
"""
import logging
logging.basicConfig(level=logging.DEBUG)

import time
import json
import os
import logging
from datetime import datetime

import requests
import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "https://api.itsm.mos.ru/requests/assigned_to_my_team"
LAST_CHECK_FILE = "last_check.json"

bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_last_check():
    try:
        with open(LAST_CHECK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return datetime.fromisoformat(data.get('last_updated', '').replace('Z', '+00:00'))
    except:
        return None


def save_last_check(dt):
    try:
        with open(LAST_CHECK_FILE, 'w', encoding='utf-8') as f:
            json.dump({'last_updated': dt.isoformat()}, f)
    except:
        pass


def get_new_requests():
    try:
        headers = {
            'Authorization': f'Bearer {os.getenv("4ME_BEARER_TOKEN")}',
            'X-4me-Account': os.getenv("4ME_ACCOUNT_ID", "sc-tech-solutions"),
            'Accept': 'application/json'
        }
        resp = requests.get(API_URL, headers=headers, params={'per_page': 30}, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"API Error: {e}")
        return []


def format_message(req):
    req_id = req.get('id')
    subject = req.get('subject', 'Без темы')
    status = req.get('status', '—')
    priority = req.get('priority') or req.get('impact', '—')
    requester = req.get('requested_by', {}).get('name', '—')
    team = req.get('team', {}).get('name', '—')
    desc = (req.get('description') or '')[:300] + ('...' if len(req.get('description', '')) > 300 else '')

    link = f"https://itsm.mos.ru/requests/{req_id}"

    return f"""🆕 <b>Новая заявка в Inbox</b>

<a href="{link}">#{req_id} — {subject}</a>

📌 Статус: <b>{status}</b>
🔥 Приоритет: <b>{priority}</b>
👤 {requester}
👥 {team}

📝 {desc}

🔗 <a href="{link}">Открыть</a>"""


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, "👋 Бот работает!\n/subscribe — подписаться\n/status — статус", parse_mode='HTML')


@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    bot.reply_to(message, "✅ Уведомления включены для этого чата!", parse_mode='HTML')


@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "✅ Бот активен", parse_mode='HTML')


def check_inbox():
    logger.info("🔍 Проверка Inbox...")
    # ... (логика проверки)
    # Пока просто логируем
    requests_list = get_new_requests()
    logger.info(f"Получено заявок: {len(requests_list)}")


if __name__ == '__main__':
    logger.info("🚀 Бот запущен")
    import schedule
    import threading

    def run_scheduler():
        schedule.every(60).seconds.do(check_inbox)
        while True:
            schedule.run_pending()
            time.sleep(1)

    threading.Thread(target=run_scheduler, daemon=True).start()
    check_inbox()

    bot.infinity_polling()