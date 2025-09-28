from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

def rtl(text):
    """اصلاح متن فارسی/عربی برای راست‌به‌چپ"""
    return get_display(arabic_reshaper.reshape(text))

if __name__ == "__main__":
    img = Image.new("RGB", (400, 200), "black")
    draw = ImageDraw.Draw(img)

    # اینجا مطمئن شو فونت تو پوشه fonts هست
    font = ImageFont.truetype("fonts/Vazirmatn-Regular.ttf", 40)

    # تست متن فارسی
    draw.text((200, 100), rtl("سلام دنیا ۱۴۰۴"), font=font, fill="white", anchor="mm")

    img.save("test.png")
    print("✅ تست ساخته شد: test.png")
