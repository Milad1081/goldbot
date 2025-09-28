# image_gen.py
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import jdatetime
import os
from scrap import get_prices

# تابع راست‌چین کامل (reshape + bidi)
def rtl(text):
    return get_display(arabic_reshaper.reshape(str(text)))

# تبدیل اعداد به فارسی
def to_persian_numbers(s):
    if not isinstance(s, str):
        s = str(s)
    return s.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))

# بدست آوردن عرض متن با دو متد ممکن
def get_text_width(draw, text, font):
    try:
        return draw.textlength(text, font=font)
    except Exception:
        return draw.textsize(text, font=font)[0]

def draw_neon_text(draw, position, text, font,
                   text_color="white", glow_color="#61a8ad", align="left"):
    x, y = position
    if align == "right":
        text_width = get_text_width(draw, text, font)
        x -= text_width

    offsets = [(-1,0), (1,0), (0,-1), (0,1)]
    for dx, dy in offsets:
        draw.text((x+dx, y+dy), text, font=font, fill=glow_color)
    draw.text((x, y), text, font=font, fill=text_color)

def draw_plain_text(draw, position, text, font, text_color="white", align="left"):
    x, y = position
    if align == "right":
        text_width = get_text_width(draw, text, font)
        x -= text_width
    draw.text((x, y), text, font=font, fill=text_color)

# تلاش برای بارگذاری فونت‌‌های فارسی داخل ریپو یا سیستم و fallback
def load_font(path_list, size, fallback_size=20):
    for p in path_list:
        try:
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
        except Exception:
            continue
    # fallback: از فونت پیش‌فرض PIL استفاده کن
    try:
        return ImageFont.load_default()
    except:
        return ImageFont.truetype("DejaVuSans.ttf", fallback_size)

def build_price_image(template_path, prices, insta, tele, output="final.png"):
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # مسیرهای ممکن فونت (در ریپو شما اگر فونت‌ها در پوشه باشند نام‌ آنها را اضافه کن)
    font_paths_heavy = ["YekanBakh-Heavy.ttf", "fonts/YekanBakh-Heavy.ttf"]
    font_paths_shabnam = ["Shabnam-Medium.ttf", "fonts/Shabnam-Medium.ttf"]
    font_paths_vazir = ["Vazirmatn-Regular.ttf", "fonts/Vazirmatn-Regular.ttf"]

    font_titr = ImageFont.truetype("YekanBakh-Heavy.ttf", 110)
    font_mid  = ImageFont.truetype("Shabnam-Medium.ttf", 35)
    font_time = ImageFont.truetype("Vazirmatn-Regular.ttf", 35)
    font_num  = ImageFont.truetype("YekanBakh-Heavy.ttf", 45)
    font_id   = ImageFont.truetype("Vazirmatn-Regular.ttf", 33)
    font_unit = ImageFont.truetype("Shabnam-Medium.ttf", 30)


    # زمان به وقت تهران (jdatetime)
    import pytz
    from datetime import datetime
    tehran = pytz.timezone("Asia/Tehran")
    now_dt = datetime.now(tehran)
    now_j = jdatetime.datetime.fromgregorian(datetime=now_dt)
    time_str = rtl(to_persian_numbers(now_j.strftime("%H:%M")))
    date_str = rtl(to_persian_numbers(now_j.strftime("%Y/%m/%d")))

    # قرار دادن زمان/تاریخ
    draw_neon_text(draw, (330, 347), time_str, font_time, align="right")
    draw_neon_text(draw, (645, 347), date_str, font_time, align="right")

    units = {
        'دلار آمریکا': "ریال",
        'یورو': "ریال",
        'درهم امارات': "ریال",
        'یوان چین': "ریال",
        'سکه امامی': "ریال",
        'ربع سکه': "ریال",
        'طلا ۱۸ عیار': "ریال",
        'انس طلا': "دلار",
        'بیت کوین': "دلار",
        'اتریوم': "دلار",
    }

    # موقعیت عمودی هر ردیف (مطابق قالب شما)
    y_positions = [445, 515, 585, 655, 750, 820, 895, 965, 1055, 1135]

    # اگر prices ترتیب متفاوت دارد، توجه کن که نمایش براساس items() انجام می‌شود
    for (label, value), y in zip(prices.items(), y_positions):
        # label نئونی راست‌چین
        draw_neon_text(draw, (645, y), rtl(label), font_mid, align="right")

        # واحد سمت چپ
        unit_text = units.get(label, "ریال")
        draw_plain_text(draw, (115, y + 10), rtl(unit_text), font_unit, align="left")

        # عدد: اگر مقدار 0 بود نشانگر "—" نمایش داده شود
        try:
            val_int = int(value)
            if val_int == 0:
                num_text = rtl("—")
            else:
                num_text = rtl(to_persian_numbers(f"{val_int:,}"))
        except Exception:
            num_text = rtl("—")

        draw_plain_text(draw, (200, y), num_text, font_num, align="left")

    # فوتر (اینستاگرام و تلگرام)
    draw_neon_text(draw, (500, 1215), rtl(tele), font_id, text_color="#000000", glow_color="#FFFFFF")
    draw_neon_text(draw, (190, 1215), rtl(insta), font_id, text_color="#000000", glow_color="#FFFFFF")

    # تیتر
    draw_neon_text(draw, (710, 195), rtl("قیمت طلا و ارز"), font_titr, text_color="white", glow_color="#00ffcc", align="right")

    img.save(output)
    return output

def generate_price_image(prices, insta="milad108", tele="market weave"):
    # این تابع ورودی می‌گیرد و مسیر عکس خروجی را برمی‌گرداند
    template = "photo_2025.png"  # مطمئن شو این فایل در ریپو هست
    return build_price_image(template, prices, insta=insta, tele=tele, output="final.png")

if __name__ == "__main__":
    p = get_prices()
    if p:
        generate_price_image(p)
        print("image generated -> final.png")
    else:
        print("No prices fetched.")
