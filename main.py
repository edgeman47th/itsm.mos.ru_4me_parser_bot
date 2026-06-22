"""
itsm.mos.ru_4me_parser_bot — максимально стабильная версия
"""

import asyncio
import logging
import json
import os
from datetime import datetime

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from service import Database

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "https://api.itsm.mos.ru/requests/assigned_to_my_team"
LAST_CHECK_FILE = "last_check.json"

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)
db = Database('./db/items.db')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("itsm.mos.ru_4me_parser_bot")


def load_last_check():
    try:
        with open(LAST_CHECK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return datetime.fromisoformat(data.get('last_updated', '').replace('Z', '+00:00'))
    except:
        return None


def save_last_check(dt: datetime):
    try:
        with open(LAST_CHECK_FILE, 'w', encoding='utf-8') as f:
            json.dump({'last_updated': dt.isoformat()}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка записи last_check: {e}")


def get_new_requests():
    try:
        headers = {
            'Authorization': f'Bearer {os.getenv("4ME_BEARER_TOKEN")}',
            'X-4me-Account': os.getenv("4ME_ACCOUNT_ID", "sc-tech-solutions"),
            'Accept': 'application/json'
        }
        params = {'per_page': 30}

        resp = requests.get(API_URL, headers=headers, params=params, timeout=20)
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

    desc = (req.get('description') or req.get('note', ''))[:350]
    if len(desc) == 350:
        desc += '...'

    link = f"https://itsm.mos.ru/requests/{req_id}"

    return f"""<b>🆕 Новая заявка в Inbox</b>

<a href="{link}">#{req_id} — {subject}</a>

📌 <b>Статус:</b> {status}
🔥 <b>Приоритет:</b> {priority}
👤 <b>Заявитель:</b> {requester}
👥 <b>Команда:</b> {team}

📝 <b>Описание:</b>
{desc}

🔗 <a href="{link}">Открыть в ITSM →</a>"""


async def check_inbox():
    logger.info("🔍 Проверка Inbox...")
    last_check = load_last_check()
    requests_list = get_new_requests()

    new_items = []
    for req in requests_list:
        try:
            updated_str = req.get('updated_at')
            if updated_str:
                updated_dt = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
