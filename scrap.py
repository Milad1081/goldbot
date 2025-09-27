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

    # قیمت انس طلا از yfinance
    gold = yf.Ticker("GC=F")
    gold_price = int(gold.history(period="1d")['Close'].iloc[-1])

    # قیمت بیت‌کوین و اتریوم از yfinance
    btc_price = int(yf.Ticker("BTC-USD").history(period="1d")['Close'].iloc[-1])
    eth_price = int(yf.Ticker("ETH-USD").history(period="1d")['Close'].iloc[-1])

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
