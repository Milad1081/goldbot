# bot.py
import os
from pyrogram import Client
from scrap import get_prices
from image_gen import generate_price_image

# خواندن اطلاعات از Env (از GitHub Secrets)
API_ID = int(os.getenv("API_ID", "0")) if os.getenv("API_ID") else None
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # می‌تواند @username یا -100... باشد

if not BOT_TOKEN or not CHANNEL_ID:
    raise RuntimeError("Missing BOT_TOKEN or CHANNEL_ID environment variables")

# اپ pyrogram
app = Client("goldbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def send_image():
    prices = get_prices()
    if not prices:
        # اگر قیمت‌ها نیامد یک پیام هشدار بفرست
        try:
            app.send_message(CHANNEL_ID, "⚠️ خطا: نتونستم قیمت‌ها رو دریافت کنم.")
        except Exception as e:
            print("Failed to send fallback message:", e)
        return

    image_path = generate_price_image(prices)

    caption_text = "📊  قیمت‌های امروز مارکت\n\n#قیمت_دلار #قیمت_طلا #قیمت_سکه"
    # راست‌چین کردن کپشن برای تلگرام (می‌توان حذف کرد یا تغییر داد)
    try:
        app.send_photo(CHANNEL_ID, photo=image_path, caption=caption_text)
    except Exception as e:
        print("Error sending photo:", e)
        # تلاش برای ارسال پیام به جای عکس
        try:
            app.send_message(CHANNEL_ID, "⚠️ ارسال عکس با خطا مواجه شد، متن قیمت‌ها:")
            # می‌توان اینجا یک پیام متنی شامل قیمت‌ها نیز ساخت و ارسال کرد
        except Exception as e2:
            print("Also failed to send fallback message:", e2)

if __name__ == "__main__":
    app.start()
    try:
        send_image()
    finally:
        app.stop()
