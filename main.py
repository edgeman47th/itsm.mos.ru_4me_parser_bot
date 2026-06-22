cat > main.py << 'EOF'
"""
itsm.mos.ru_4me_parser_bot — стабильная версия
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
            return datetime.fromisoformat(data['last_updated'].replace('Z', '+00:00'))
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
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
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

🔗 <a href="{link}">Открыть →</a>"""


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
                if last_check is None or updated_dt > last_check:
                    new_items.append(req)
        except:
            continue

    if not new_items:
        return

    subscribers = db.get_subscribers()
    for req in new_items:
        text = format_message(req)
        for user_id in subscribers:
            try:
                await bot.send_message(chat_id=user_id, text=text, disable_web_page_preview=True)
                logger.info(f"Отправлено уведомление о заявке #{req.get('id')}")
            except Exception as e:
                logger.warning(f"Не отправлено {user_id}: {e}")

    if new_items:
        latest = max((datetime.fromisoformat(r['updated_at'].replace('Z','+00:00')) 
                     for r in new_items if r.get('updated_at')), default=None)
        if latest:
            save_last_check(latest)


# ================== КОМАНДЫ ==================
@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: types.Message):
    await message.reply("👋 <b>itsm.mos.ru_4me_parser_bot</b>\n\n"
                       "/subscribe — подписаться\n"
                       "/unsubscribe — отписаться\n"
                       "/status — проверить статус")


@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    db.add_subscriber(message.from_user.id)
    await message.reply("✅ Вы подписаны на новые заявки!")


@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    db.remove_subscriber(message.from_user.id)
    await message.reply("❌ Вы отписались.")


@dp.message_handler(commands=['status'])
async def status_cmd(message: types.Message):
    await message.reply("✅ Бот активен и проверяет Inbox каждые 60 секунд.")


async def main():
    logger.info("🚀 itsm.mos.ru_4me_parser_bot запущен")

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(check_inbox, 'interval', seconds=60)
    scheduler.start()

    asyncio.create_task(check_inbox())   # первая проверка

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
EOF