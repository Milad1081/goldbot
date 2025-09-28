# scrap.py
import os
import requests
from bs4 import BeautifulSoup
import yfinance as yf

def clean(x):
    try:
        return int(str(x).replace(",", ""))
    except Exception:
        return 0

def fetch_gold_from_ninjas(api_key):
    """Get gold price (ounce) from API-Ninjas"""
    if not api_key:
        return None
    try:
        r = requests.get(
            "https://api.api-ninjas.com/v1/goldprice",
            headers={"X-Api-Key": api_key},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            return float(data.get("price") or data.get("value") or data.get("rate"))
        else:
            print("[ninjas gold] http error:", r.status_code, r.text[:200])
    except Exception as e:
        print("Exception ninjas gold:", e)
    return None

def get_prices():
    # ---- دلار و سکه و ... از tgju ----
    try:
        page = requests.get("https://www.tgju.org", timeout=10)
    except Exception as e:
        print("Error requesting tgju:", e)
        return None
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

    prices = {}
    prices['دلار آمریکا'] = get_data_price("price_dollar_rl")
    prices['درهم امارات'] = get_data_price("price_aed")
    prices['یورو'] = get_data_price("price_eur")
    prices['یوان چین'] = get_data_price("price_cny")
    prices['سکه امامی'] = get_data_price("retail_sekee")
    prices['ربع سکه'] = get_data_price("retail_rob")
    prices['طلا ۱۸ عیار'] = get_data_price("geram18")

    # ---- انس طلا از API-Ninjas ----
    api_key = os.getenv("API_NINJAS_KEY")
    gold_val = fetch_gold_from_ninjas(api_key)
    prices['انس طلا'] = int(gold_val) if gold_val else 0

    # ---- بیت‌کوین و اتریوم از yfinance ----
    try:
        btc_price = yf.Ticker("BTC-USD").history(period="1d")
        prices['بیت کوین'] = int(btc_price['Close'].iloc[-1]) if not btc_price.empty else 0
    except:
        prices['بیت کوین'] = 0

    try:
        eth_price = yf.Ticker("ETH-USD").history(period="1d")
        prices['اتریوم'] = int(eth_price['Close'].iloc[-1]) if not eth_price.empty else 0
    except:
        prices['اتریوم'] = 0

    print("Final prices:", prices)
    return prices

if __name__ == "__main__":
    print(get_prices())
