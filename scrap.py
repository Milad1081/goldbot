import requests
from bs4 import BeautifulSoup
import yfinance as yf

def get_prices():
    page = requests.get("https://www.tgju.org")
    if page.status_code != 200:
        return None

    soup = BeautifulSoup(page.text, "html.parser")

    def clean(x):
        try:
            return int(x.replace(",", ""))
        except:
            return 0

    def safe_price(ticker, period="1d"):
        try:
            history = yf.Ticker(ticker).history(period=period)
            if not history.empty:
                return int(history['Close'].iloc[-1])
        except Exception as e:
            print(f"⚠️ Error fetching {ticker}: {e}")
        return 0

    # قیمت انس طلا، بیت‌کوین و اتریوم
    gold_price = safe_price("GC=F")
    btc_price = safe_price("BTC-USD")
    eth_price = safe_price("ETH-USD")

    return {
        'دلار آمریکا': clean(soup.find("tr", {"data-market-row": "price_dollar_rl"})["data-price"]),
        'درهم امارات': clean(soup.find("tr", {"data-market-row": "price_aed"})["data-price"]),
        'یورو': clean(soup.find("tr", {"data-market-row": "price_eur"})["data-price"]),
        'یوان چین': clean(soup.find("tr", {"data-market-row": "price_cny"})["data-price"]),

        'سکه امامی': clean(soup.find("tr", {"data-market-row": "retail_sekee"})["data-price"]),
        'ربع سکه': clean(soup.find("tr", {"data-market-row": "retail_rob"})["data-price"]),
        'طلا ۱۸ عیار': clean(soup.find("tr", {"data-market-row": "geram18"})["data-price"]),
        'انس طلا': gold_price,

        'بیت کوین': btc_price,
        'اتریوم': eth_price,
    }
