from apscheduler.schedulers.asyncio import AsyncIOScheduler
from news_parser import fetch_news
from news_processor import process_news
from main import db


async def collect_and_process_news():
    news_list = fetch_news()
    for article in news_list:
        title = article["title"]
        description = article["description"] or ""
        url = article["url"]

        summary = process_news(title, description)
        db.execute("""
            INSERT INTO news (title, summary, url)
            VALUES (%s, %s, %s)
            ON CONFLICT (url) DO NOTHING;
        """, (title, summary, url))

# scheduler = AsyncIOScheduler()
# scheduler.add_job(collect_and_process_news, "cron", hour="8,20")
#
