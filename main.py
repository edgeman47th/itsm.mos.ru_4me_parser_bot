import asyncio
import logging
import json
from datetime import datetime

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from parser import ItemParser
from service import Database

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LAST_CHECK_FILE = "last_check.json"

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)
db = Database('./db/items.db')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_last_check():
    try:
        with open(LAST_CHECK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return datetime.fromisoformat(data['last_updated'].replace('Z', '+00:00'))
    except:
        return None


def save_last_check(dt):
    with open(LAST_CHECK_FILE, 'w', encoding='utf-8') as f:
        json.dump({'last_updated': dt.isoformat()}, f)


def get_new_requests():
    last_check = load_last_check()
    all_requests = ItemParser.check_new_requests()  # твой парсер
    
    new_requests = []
    for req in all_requests:
        try:
            updated = datetime.fromisoformat(req.get('updated_at', '').replace('Z', '+00:00'))
            if not last_check or updated > last_check:
                new_requests.append(req)
        except:
            continue
    return new_requests


async def notify_new_items():
    new_requests = get_new_requests()
    if not new_requests:
        return

    subscribers = db.get_subscribers()
    for req in new_requests:
        message = format_message(req)
        for user_id in subscribers:
            try:
                await bot.send_message(chat_id=user_id, text=message, disable_web_page_preview=True)
            except Exception as e:
                logger.error(f"Ошибка отправки {user_id}: {e}")

    # Обновляем время
    if new_requests:
        latest = max(datetime.fromisoformat(r['updated_at'].replace('Z','+00:00')) for r in new_requests if r.get('updated_at'))
        save_last_check(latest)


def format_message(req):
    req_id = req.get('id')
    subject = req.get('subject', 'Без темы')
    status = req.get('status')
    priority = req.get('impact') or '—'
    team = req.get('team', {}).get('name', '—')
    next_target = req.get('next_target_at', '—')
    desc = (req.get('description') or '')[:350] + ('...' if len(req.get('description', '')) > 350 else '')

    link = f"https://itsm.mos.ru/requests/{req_id}"

    return f"""<b>🆕 Новая заявка в Inbox</b>

<a href="{link}">#{req_id} — {subject}</a>

📌 Статус: <b>{status}</b>
🔥 Приоритет: <b>{priority}</b>
👥 Команда: <b>{team}</b>
⏰ Дедлайн: <b>{next_target}</b>

📝 Описание:
{desc}

🔗 <a href="{link}">Открыть заявку</a>"""


# Команды
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    db.add_subscriber(message.from_user.id)
    await message.reply("✅ Вы подписаны на новые заявки в Inbox!")

@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    db.remove_subscriber(message.from_user.id)
    await message.reply("❌ Вы отписались.")

@dp.message_handler(commands=['status'])
async def status(message: types.Message):
    await message.reply("✅ Бот работает. Проверяет Inbox каждые 60 секунд.")


async def main():
    logger.info("🚀 itsm.mos.ru_4me_parser_bot запущен")
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(notify_new_items, 'interval', seconds=60)
    scheduler.start()

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())