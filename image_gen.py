from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

def rtl(text):
    return get_display(arabic_reshaper.reshape(text))

img = Image.new("RGB", (800, 200), "black")
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("fonts/Shabnam-Medium.ttf", 60)

draw.text((700, 50), rtl("دلار آمریکا"), font=font, fill="white", anchor="ra")  
# anchor="ra" یعنی راست‌چین بشه

img.save("test.png")
