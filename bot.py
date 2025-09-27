from pyrogram import Client
from apscheduler.schedulers.background import BackgroundScheduler
from scrap import get_prices
from image_gen import generate_price_image
from info import BOT_TOKEN, API_ID, API_HASH, CHANNEL_ID

app = Client("goldbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def send_image():
    prices = get_prices()
    if prices:
        image_path = generate_price_image(prices)
        caption = (
            "📊  قیمت‌های امروز مارکت\n\n"
            "#قیمت_دلار #قیمت_طلا #قیمت_سکه"
        )
        app.send_photo(CHANNEL_ID, photo=image_path, caption=caption)

if __name__ == "__main__":
    app.start()

    # ---- زمان‌بندی با APScheduler ----
    scheduler = BackgroundScheduler(timezone="Asia/Tehran")
    scheduler.add_job(send_image, 'cron', hour=9, minute=0)
    scheduler.add_job(send_image, 'cron', hour=13, minute=0)
    scheduler.add_job(send_image, 'cron', hour=19, minute=0)
    scheduler.start()

    print("ربات فعال است و طبق برنامه زمان‌بندی پیام ارسال می‌کند...")

    try:
        # نگه داشتن برنامه در حال اجرا
        import time
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        app.stop()
