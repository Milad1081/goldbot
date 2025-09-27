from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import jdatetime
from scrap import get_prices  # قیمت‌ها از اینجا میاد

# ---- راست‌چین فارسی ----
def rtl(text):
    return get_display(arabic_reshaper.reshape(text))

# ---- تبدیل اعداد انگلیسی به فارسی ----
def to_persian_numbers(s):
    if not isinstance(s, str):
        s = str(s)
    return s.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))

# ---- به دست آوردن عرض متن ----
def get_text_width(draw, text, font):
    try:
        return draw.textlength(text, font=font)
    except Exception:
        return draw.textsize(text, font=font)[0]

# ---- افکت نئونی ----
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

# ---- متن ساده بدون افکت ----
def draw_plain_text(draw, position, text, font, text_color="white", align="left"):
    x, y = position
    if align == "right":
        text_width = get_text_width(draw, text, font)
        x -= text_width
    draw.text((x, y), text, font=font, fill=text_color)

# ---- ساخت تصویر نهایی ----
def build_price_image(template_path, prices, insta, tele, output="final.png"):
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # فونت‌ها
    font_titr = ImageFont.truetype("YekanBakh-Heavy.ttf", 110)
    font_mid = ImageFont.truetype("Shabnam-Medium.ttf", 35)
    font_time = ImageFont.truetype("Vazirmatn-Regular.ttf", 35)
    font_num = ImageFont.truetype("YekanBakh-Heavy.ttf", 45)
    font_id = ImageFont.truetype("Vazirmatn-Regular.ttf", 33)
    font_unit = ImageFont.truetype("Shabnam-Medium.ttf", 30)

    # تاریخ و ساعت شمسی
    now = jdatetime.datetime.now()
    time_str = to_persian_numbers(now.strftime("%H:%M"))
    date_str = to_persian_numbers(now.strftime("%Y/%m/%d"))

    draw_neon_text(draw, (330, 347), rtl(time_str), font_time, align="right")
    draw_neon_text(draw, (645, 347), rtl(date_str), font_time, align="right")

    # واحدها دستی
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

    # موقعیت‌های عمودی هر ردیف
    y_positions = [445, 515, 585, 655, 750, 820, 895, 965, 1055, 1135]

    for (label, value), y in zip(prices.items(), y_positions):
        # رسم لیبل با نئون
        draw_neon_text(draw, (645, y), rtl(label), font_mid, align="right")

        # واحد سمت چپ عدد، با فونت مناسب و راست چین
        unit_text = units.get(label, "ریال")
        draw_plain_text(draw, (115, y + 10), rtl(unit_text), font_unit, text_color="white", align="left")

        # عدد فارسی
        num_text = to_persian_numbers(f"{int(value):,}")
        draw_plain_text(draw, (200, y), num_text, font_num, text_color="white", align="left")

    # فوتر
    draw_neon_text(draw, (500, 1215), tele, font_id, text_color="#000000", glow_color="#FFFFFF")
    draw_neon_text(draw, (190, 1215), insta, font_id, text_color="#000000", glow_color="#FFFFFF")

    # تیتر
    draw_neon_text(draw, (710, 195), rtl("قیمت طلا و ارز"), font_titr, text_color="white", glow_color="#00ffcc", align="right")

    img.save(output)
    return output

# ---- تابع اصلی ----
def generate_price_image(prices, insta="milad108", tele="market weave"):
    return build_price_image(
        "photo_2025.png",
        prices,
        insta=insta,
        tele=tele,
        output="final.png"
    )

# ---- اجرا برای تست ----
if __name__ == "__main__":
    prices = get_prices()
    if prices:
        generate_price_image(prices)
