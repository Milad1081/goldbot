import os
import requests
from bs4 import BeautifulSoup
import yfinance as yf

API_KEY = "BVBG2X768S2DX1M4"  # کلید رایگان خودت رو اینجا بذار

def clean(x):
    """تبدیل متن عددی به int"""
    try:
        return int(str(x).replace(",", "").strip())
    except Exception:
        return 0


# --- انس جهانی طلا از Alpha Vantage ---
def fetch_gold_ounce():
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "XAU",
            "to_currency": "USD",
            "apikey": API_KEY
        }
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if "Realtime Currency Exchange Rate" in data:
                price = data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
                return float(price)
        print("[AlphaVantage] invalid response:", data)
    except Exception as e:
        print("[AlphaVantage] error:", e)
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

    # --- انس جهانی طلا از Alpha Vantage ---
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
