from PIL import Image, ImageDraw, ImageFont
import jdatetime
import os
from scrap import get_prices


# --- اعداد فارسی ---
def to_persian_numbers(s):
    if not isinstance(s, str):
        s = str(s)
    return s.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def get_text_width(draw, text, font):
    try:
        return draw.textlength(text, font=font)
    except Exception:
        return draw.textsize(text, font=font)[0]


# --- ترسیم متن ---
def draw_neon_text(draw, position, text, font, text_color="white", glow_color="#61a8ad", align="left"):
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


# --- بارگذاری فونت‌ها ---
def load_font(filename, size):
    path = os.path.join("fonts", filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Font not found: {path}")
    return ImageFont.truetype(path, size)


# --- ساخت تصویر ---
def build_price_image(template_path, prices, insta, tele, output="final.png"):
    print("Building image, template:", template_path)
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # بارگذاری فونت‌ها
    font_titr = load_font("YekanBakh-Heavy.ttf", 110)
    font_mid  = load_font("Shabnam-Medium.ttf", 35)
    font_time = load_font("Vazirmatn-Regular.ttf", 35)
    font_num  = load_font("YekanBakh-Heavy.ttf", 45)
    font_id   = load_font("Vazirmatn-Regular.ttf", 33)
    font_unit = load_font("Shabnam-Medium.ttf", 30)

    # زمان و تاریخ
    import pytz
    from datetime import datetime
    tehran = pytz.timezone("Asia/Tehran")
    now_dt = datetime.now(tehran)
    now_j = jdatetime.datetime.fromgregorian(datetime=now_dt)

    time_str = to_persian_numbers(now_j.strftime("%H:%M"))
    date_str = to_persian_numbers(now_j.strftime("%Y/%m/%d"))

    draw_neon_text(draw, (330, 347), time_str, font_time, align="right")
    draw_neon_text(draw, (645, 347), date_str, font_time, align="right")

    # واحدها
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

    # موقعیت‌ها
    y_positions = [445, 515, 585, 655, 750, 820, 895, 965, 1055, 1135]

    for (label, value), y in zip(prices.items(), y_positions):
        # برچسب راست‌چین (متن فارسی مستقیم)
        draw_neon_text(draw, (645, y), label, font_mid, align="right")

        # واحد
        unit_text = units.get(label, "ریال")
        draw_plain_text(draw, (115, y + 10), unit_text, font_unit, align="left")

        # عدد
        try:
            val_int = int(value)
            if val_int == 0:
                num_text = "—"
            else:
                num_text = to_persian_numbers(f"{val_int:,}")
        except Exception:
            num_text = "—"

        draw_plain_text(draw, (200, y), num_text, font_num, align="left")

    # فوتر
    draw_neon_text(draw, (500, 1215), tele, font_id, text_color="#000000", glow_color="#FFFFFF")
    draw_neon_text(draw, (190, 1215), insta, font_id, text_color="#000000", glow_color="#FFFFFF")

    # تیتر
    draw_neon_text(draw, (710, 195), "قیمت طلا و ارز", font_titr, text_color="white", glow_color="#00ffcc", align="right")

    img.save(output)
    print("Saved image:", output)
    return output


def generate_price_image(prices, insta="milad108", tele="market weave"):
    template = "photo_2025.png"
    if not os.path.exists(template):
        raise FileNotFoundError(f"Template not found: {template}")
    return build_price_image(template, prices, insta=insta, tele=tele, output="final.png")


if __name__ == "__main__":
    p = get_prices()
    if p:
        generate_price_image(p)
        print("image generated -> final.png")
    else:
        print("No prices fetched.")
