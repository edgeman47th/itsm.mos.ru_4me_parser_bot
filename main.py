import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parser import ItemParser
from service import Database
from datetime import datetime
from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

db = Database('./db/items.db')

async def notify_new_items():
    new_requests = ItemParser.check_new_requests()
    if len(new_requests)==0:
        return
    all_users= db.get_subscribers()
    for deadline in new_requests:
        for user_id in all_users:
            try:
                deadline_date =  datetime.fromisoformat(deadline.get('next_target_at')[:-6])
                message= f"Уведомление: Новый запрос: №{deadline.get('id')}- {deadline.get('subject')}\nДедлайн для запроса наступит в {deadline_date}"
                await bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
            except Exception as e:
                print(e)
    
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    user_id = message.from_user.id
    db.add_subscriber(user_id)
    await message.reply("Вы подписаны на уведомления о новых сообщениях.")

@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    user_id = message.from_user.id
    db.remove_subscriber(user_id)
    await message.reply("Вы отписались от уведомлений.")

@dp.message_handler(commands=['test'])
async def unsubscribe(message: types.Message):
    await message.reply("работает")
        

async def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(notify_new_items, 'interval', seconds=60, misfire_grace_time=200)  # Проверяем каждые 120 секунд
    scheduler.start()

async def main():
    logging.basicConfig(
        filename="debug.log",
        filemode="w",
        level=logging.DEBUG,
        encoding='UTF-8',
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    await start_scheduler()
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
