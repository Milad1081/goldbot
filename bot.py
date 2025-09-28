from pyrogram import Client
from scrap import get_prices
from image_gen import generate_price_image
import os

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

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
    else:
        app.send_message(CHANNEL_ID, "⚠️ نتونستم قیمت‌ها رو دریافت کنم.")

if __name__ == "__main__":
    app.start()
    send_image()
    app.stop()
