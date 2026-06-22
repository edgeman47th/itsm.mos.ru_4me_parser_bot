"""
itsm.mos.ru_4me_parser_bot — максимально простая стабильная версия
"""

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
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # можно оставить пустым

bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LAST_CHECK_FILE = "last_check.json"
API_URL = "https://api.itsm.mos.ru/requests/assigned_to_my_team"


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
            json.dump({'last_updated': dt.isoformat()}, f, ensure_ascii=False)
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
    desc = (req.get('description') or req.get('note', ''))[:300] + ('...' if len(req.get('description', '')) > 300 else '')

    link = f"https://itsm.mos.ru/requests/{req_id}"

    return f"""🆕 <b>Новая заявка в Inbox</b>

<a href="{link}">#{req_id} — {subject}</a>

📌 Статус: <b>{status}</b>
🔥 Приоритет: <b>{priority}</b>
👤 Заявитель: <b>{requester}</b>
👥 Команда: <b>{team}</b>

📝 {desc}

🔗 <a href="{link}">Открыть</a>"""


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, "👋 Бот запущен.\n/subscribe — включить уведомления\n/status — проверить", parse_mode='HTML')


@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "✅ Бот работает", parse_mode='HTML')


@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    bot.reply_to(message, "✅ Уведомления включены для этого чата!", parse_mode='HTML')
    logger.info(f"Подписка от пользователя {message.chat.id}")


def check_inbox():
    logger.info("Проверка Inbox...")
    last_check = load_last_check()
    requests_list = get_new_requests()

    new_items = []
    for req in requests_list:
        try:
            updated_str = req.get('updated_at')
            if updated_str:
                updated_dt = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                if last_check is None or updated_dt > last_check:
                    new_items.append(req)
        except:
            continue

    if new_items:
        for req in new_items:
            text = format_message(req)
            try:
                bot.send_message(CHAT_ID or 7967969403, text, parse_mode='HTML', disable_web_page_preview=True)
                logger.info(f"Отправлено уведомление #{req.get('id')}")
            except Exception as e:
                logger.error(f"Ошибка отправки: {e}")

        if new_items:
            latest = max((datetime.fromisoformat(r['updated_at'].replace('Z','+00:00')) for r in new_items if r.get('updated_at')), default=None)
            if latest:
                save_last_check(latest)


if __name__ == '__main__':
    logger.info("🚀 itsm.mos.ru_4me_parser_bot запущен")
    import schedule
    import threading

    def run():
        schedule.every(60).seconds.do(check_inbox)
        while True:
            schedule.run_pending()
            time.sleep(1)

    threading.Thread(target=run, daemon=True).start()
    check_inbox()  # первая проверка

    bot.infinity_polling()