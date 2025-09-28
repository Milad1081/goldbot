# scrap.py
import os
import requests
from bs4 import BeautifulSoup

# -------- helpers --------
def clean(x):
    try:
        return int(x.replace(",", ""))
    except Exception:
        return 0

# استفاده از API Ninjas برای انس طلا و رمزارزها
def fetch_gold_from_ninjas(api_key):
    if not api_key:
        return 0
    url = "https://api.api-ninjas.com/v1/goldprice"
    headers = {"X-Api-Key": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # مقدار ممکن است در کلید "price" یا مشابه باشد
            return float(data.get("price", 0) or data.get("value", 0) or 0)
        else:
            print("Ninjas goldprice error:", r.status_code, r.text)
    except Exception as e:
        print("Exception fetching gold from Ninjas:", e)
    return 0

def fetch_crypto_from_ninjas(api_key, symbol):
    if not api_key:
        return 0
    url = f"https://api.api-ninjas.com/v1/cryptoprice?symbol={symbol}"
    headers = {"X-Api-Key": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return float(data.get("price", 0) or 0)
        else:
            print(f"Ninjas cryptoprice {symbol} error:", r.status_code, r.text)
    except Exception as e:
        print(f"Exception fetching {symbol} from Ninjas:", e)
    return 0

# -------- main --------
def get_prices():
    # 1) اسکرپ از tgju برای قیمت‌های داخلی (ارز، سکه، طلا18)
    try:
        page = requests.get("https://www.tgju.org", timeout=10)
    except Exception as e:
        print("Error requesting tgju:", e)
        return None

    if page.status_code != 200:
        print("tgju returned status:", page.status_code)
        return None

    soup = BeautifulSoup(page.text, "html.parser")

    try:
        prices = {
            'دلار آمریکا': clean(soup.find("tr", {"data-market-row": "price_dollar_rl"})["data-price"]),
            'درهم امارات': clean(soup.find("tr", {"data-market-row": "price_aed"})["data-price"]),
            'یورو': clean(soup.find("tr", {"data-market-row": "price_eur"})["data-price"]),
            'یوان چین': clean(soup.find("tr", {"data-market-row": "price_cny"})["data-price"]),

            'سکه امامی': clean(soup.find("tr", {"data-market-row": "retail_sekee"})["data-price"]),
            'ربع سکه': clean(soup.find("tr", {"data-market-row": "retail_rob"})["data-price"]),
            'طلا ۱۸ عیار': clean(soup.find("tr", {"data-market-row": "geram18"})["data-price"]),
        }
    except Exception as e:
        print("Error parsing tgju HTML:", e)
        return None

    # 2) انس طلا و رمزارزها از API Ninjas (needs API_NINJAS_KEY)
    api_key = os.getenv("API_NINJAS_KEY", "")
    gold_price = fetch_gold_from_ninjas(api_key)
    btc_price = fetch_crypto_from_ninjas(api_key, "BTC")
    eth_price = fetch_crypto_from_ninjas(api_key, "ETH")

    # اگر عدد صفر است یعنی نتونستیم بخونیم => مقدار 0 می‌گذاریم (image_gen آن را نمایش خواهد داد)
    prices['انس طلا'] = gold_price or 0
    prices['بیت کوین'] = btc_price or 0
    prices['اتریوم'] = eth_price or 0

    return prices

# debug
if __name__ == "__main__":
    print(get_prices())
