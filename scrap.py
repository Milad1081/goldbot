import os
import requests
from bs4 import BeautifulSoup
import yfinance as yf

def clean(x):
    """تبدیل متن عددی به int"""
    try:
        return int(str(x).replace(",", "").strip())
    except Exception:
        return 0


# --- انس جهانی طلا از metals.live ---
def fetch_gold_ounce():
    try:
        r = requests.get("https://api.metals.live/v1/spot", timeout=10)
        if r.status_code == 200:
            data = r.json()
            for item in data:
                if "gold" in item:
                    return float(item["gold"])
        print("[metals.live] invalid response")
    except Exception as e:
        print("[metals.live] error:", e)
    return None


# --- تابع اصلی ---
def get_prices():
    prices = {}

    # --- قیمت‌ها از TGJU ---
    try:
        page = requests.get("https://www.tgju.org", timeout=10)
        if page.status_code != 200:
            print("tgju status:", page.status_code)
            return None
        soup = BeautifulSoup(page.text, "html.parser")

        def get_data_price(tr_key):
            try:
                el = soup.find("tr", {"data-market-row": tr_key})
                if el and el.has_attr("data-price"):
                    return clean(el["data-price"])
            except Exception:
                pass
            return 0

        prices['دلار آمریکا'] = get_data_price("price_dollar_rl")
        prices['درهم امارات'] = get_data_price("price_aed")
        prices['یورو'] = get_data_price("price_eur")
        prices['یوان چین'] = get_data_price("price_cny")
        prices['سکه امامی'] = get_data_price("retail_sekee")
        prices['ربع سکه'] = get_data_price("retail_rob")
        prices['طلا ۱۸ عیار'] = get_data_price("geram18")

    except Exception as e:
        print("Error fetching TGJU:", e)

    # --- انس جهانی طلا از metals.live ---
    gold_ounce = fetch_gold_ounce()
    prices['انس طلا'] = int(gold_ounce) if gold_ounce else 0

    # --- بیت کوین ---
    try:
        btc = yf.Ticker("BTC-USD").history(period="1d")
        prices['بیت کوین'] = int(btc['Close'].iloc[-1]) if not btc.empty else 0
    except Exception as e:
        print("BTC error:", e)
        prices['بیت کوین'] = 0

    # --- اتریوم ---
    try:
        eth = yf.Ticker("ETH-USD").history(period="1d")
        prices['اتریوم'] = int(eth['Close'].iloc[-1]) if not eth.empty else 0
    except Exception as e:
        print("ETH error:", e)
        prices['اتریوم'] = 0

    print("✅ Final prices:", prices)
    return prices


if __name__ == "__main__":
    print(get_prices())
