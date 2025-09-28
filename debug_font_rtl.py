# debug_font_rtl.py
import os
import sys
import platform
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

def rtl(text: str) -> str:
    return get_display(arabic_reshaper.reshape(str(text)))

print("=== ENV & PYTHON ===")
print("cwd:", os.getcwd())
print("platform:", platform.platform())
print("python:", sys.version.replace("\n"," "))
print()

print("=== ROOT files ===")
for p in sorted(os.listdir(".")):
    print(p)
print()

fonts_dir = "fonts"
print("=== fonts dir exists? ===", os.path.exists(fonts_dir))
if os.path.exists(fonts_dir):
    print("=== fonts list ===")
    for f in sorted(os.listdir(fonts_dir)):
        print(" -", f)
print()

# pip freeze (best-effort)
print("=== pip freeze (top lines) ===")
try:
    import pkg_resources
    for i, d in enumerate(sorted(pkg_resources.working_set, key=lambda r:r.project_name.lower())):
        print(d.project_name, d.version)
        if i > 60:
            break
except Exception as e:
    print("pip freeze failed:", e)
print()

# test rtl transform
tests = ["دلار آمریکا", "قیمت طلا و ارز", "طلا ۱۸ عیار", "سکه امامی"]
print("=== rtl outputs ===")
for t in tests:
    print(t, "->", repr(rtl(t)))
print()

# try loading each font and check glyph support for some Arabic letters
check_chars = "داللاطاﺍر"  # a small set including alef/beh-like shapes and dal/lam/teh
if os.path.exists(fonts_dir):
    for fname in sorted(os.listdir(fonts_dir)):
        path = os.path.join(fonts_dir, fname)
        try:
            f = ImageFont.truetype(path, 40)
            print(f"[FONT LOAD OK] {fname}")
            # create mask for some chars to see if glyph exists
            for ch in ["د", "ل", "ا", "ر", "ی", "ط"]:
                try:
                    m = f.getmask(ch)
                    has = m.getbbox() is not None
                except Exception as e:
                    has = False
                print(f"   glyph '{ch}':", "YES" if has else "NO")
            # draw a quick test image with raw and rtl text
            img = Image.new("RGB", (900, 140), (20,20,20))
            d = ImageDraw.Draw(img)
            # raw (no rtl)
            try:
                d.text((10,10), "RAW: " + "دلار آمریکا", font=f, fill="white", anchor=None)
            except TypeError:
                d.text((10,10), "RAW: " + "دلار آمریکا", font=f, fill="white")
            # rtl (reshaped + bidi)
            rtl_text = rtl("دلار آمریکا")
            try:
                d.text((10,60), "RTL: " + rtl_text, font=f, fill="yellow")
            except TypeError:
                d.text((10,60), "RTL: " + rtl_text, font=f, fill="yellow")
            out = f"debug_{fname}.png"
            img.save(out)
            print("   wrote:", out)
        except Exception as e:
            print(f"[FONT LOAD FAIL] {fname} ->", e)
print()

# Also create an image using a guaranteed-good font name if exists: Vazirmatn-Regular.ttf
fallback = os.path.join(fonts_dir, "Vazirmatn-Regular.ttf")
if os.path.exists(fallback):
    try:
        f = ImageFont.truetype(fallback, 48)
        img = Image.new("RGB", (900, 200), (30,30,30))
        d = ImageDraw.Draw(img)
        try:
            d.text((880,50), rtl("دلار آمریکا"), font=f, fill="white", anchor="ra")
            d.text((880,120), "۱۲۳۴۵۶", font=f, fill="cyan", anchor="ra")
        except TypeError:
            # no anchor support
            d.text((600,50), rtl("دلار آمریکا"), font=f, fill="white")
            d.text((600,120), "۱۲۳۴۵۶", font=f, fill="cyan")
        img.save("debug_vazir.png")
        print("wrote debug_vazir.png")
    except Exception as e:
        print("failed create debug_vazir:", e)
else:
    print("Vazirmatn-Regular.ttf not found in fonts/ (optional test skipped)")

print("\n=== DONE ===\n")
