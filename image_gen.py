# image_gen.py
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import jdatetime
import os
from scrap import get_prices

def rtl(text: str) -> str:
    return get_display(arabic_reshaper.reshape(str(text)))

def to_persian_numbers(s):
    if not isinstance(s, str):
        s = str(s)
    return s.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))

def get_text_width(draw, text, font):
    try:
        return draw.textlength(text, font=font)
    except Exception:
        return draw.textsize(text, font=font)[0]

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

def try_load_font(names, size):
    """Try multiple font filenames (in repo root or fonts/). Return ImageFont or None."""
    candidates = []
    for n in names:
        candidates.append(n)
        candidates.append(os.path.join("fonts", n))
    for p in candidates:
        try:
            if os.path.exists(p):
                f = ImageFont.truetype(p, size)
                print(f"[font] loaded {p}")
                return f
        except Exception as e:
            print(f"[font] failed load {p}: {e}")
    print(f"[font] none of {names} found; falling back to default font")
    try:
        return ImageFont.load_default()
    except:
        return ImageFont.truetype("DejaVuSans.ttf", size)

def build_price_image(template_path, prices, insta, tele, output="final.png"):
    print("Building image, template:", template_path)
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # load fonts (try repo root then fonts/)
    font_titr = try_load_font(["YekanBakh-Heavy.ttf"], 110)
    font_mid  = try_load_font(["Shabnam-Medium.ttf"], 35)
    font_time = try_load_font(["Vazirmatn-Regular.ttf"], 35)
    font_num  = try_load_font(["YekanBakh-Heavy.ttf"], 45)
    font_id   = try_load_font(["Vazirmatn-Regular.ttf"], 33)
    font_unit = try_load_font(["Shabnam-Medium.ttf"], 30)

    # time Tehran
    import pytz
    from datetime import datetime
    tehran = pytz.timezone("Asia/Tehran")
    now_dt = datetime.now(tehran)
    now_j = jdatetime.datetime.fromgregorian(datetime=now_dt)
    time_str = to_persian_numbers(now_j.strftime("%H:%M"))
    date_str = to_persian_numbers(now_j.strftime("%Y/%m/%d"))

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

    y_positions = [445, 515, 585, 655, 750, 820, 895, 965, 1055, 1135]

    for (label, value), y in zip(prices.items(), y_positions):
        # label -> rtl
        draw_neon_text(draw, (645, y), rtl(label), font_mid, align="right")

        # unit -> rtl
        unit_text = units.get(label, "ریال")
        draw_plain_text(draw, (115, y + 10), rtl(unit_text), font_unit, align="left")

        # number: if 0 -> "—" else formatted Persian numbers (no rtl)
        try:
            val_int = int(value)
            if val_int == 0:
                num_text = "—"
            else:
                num_text = to_persian_numbers(f"{val_int:,}")
        except Exception:
            num_text = "—"

        draw_plain_text(draw, (200, y), num_text, font_num, align="left")

    # footer: insta & tele (these are short labels — rtl them)
    draw_neon_text(draw, (500, 1215), rtl(tele), font_id, text_color="#000000", glow_color="#FFFFFF")
    draw_neon_text(draw, (190, 1215), rtl(insta), font_id, text_color="#000000", glow_color="#FFFFFF")

    # title
    draw_neon_text(draw, (710, 195), rtl("قیمت طلا و ارز"), font_titr, text_color="white", glow_color="#00ffcc", align="right")

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
