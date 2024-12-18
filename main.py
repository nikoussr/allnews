import asyncio
import logging
from aiogram import Bot, Dispatcher
import handlers.start_handler
from configs import TOKEN
from aiogram.fsm.storage.memory import MemoryStorage
from database.db import Database

bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot)
db = Database()


async def fetch_and_send_news(chat_id):
    """Функция парсинга и отправки новостей"""
    from backend.news_parser import fetch_news
    from backend.news_processor import process_news

    news_list = fetch_news()
    if not news_list:
        await bot.send_message(chat_id, "Не удалось найти новости. Попробуйте позже.")
        return

    for article in news_list[:5]:  # Берем максимум 5 новостей
        title = article["title"]
        description = article["description"] or ""
        url = article["url"]

        summary = process_news(title, description)
        print(summary)
        await db.execute("INSERT INTO news (title, summary, url) VALUES ($1, $2, $3)", title, summary, url)
        # Отправляем новость пользователю
        await bot.send_message(chat_id, f"<b>{title}</b>\n{summary}\n<a href='{url}'>Читать далее</a>",
                               parse_mode="HTML")


async def main():
    await db.connect('postgresql://postgres:postgrespostgres@localhost/allnews')
    await bot.delete_webhook()
    dp.include_router(handlers.start_handler.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('EXIT')
