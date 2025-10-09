import requests
from bs4 import BeautifulSoup
import yfinance as yf

def clean(x):
    """تبدیل متن عددی به int"""
    try:
        return int(str(x).replace(",", "").strip())
    except Exception:
        return 0

def get_gold_ounce():
    """دریافت قیمت انس طلا از منابع معتبر"""
    try:
        # روش 1: از Financial Modeling Prep (رایگان)
        url = "https://financialmodelingprep.com/api/v3/quote/XAUUSD?apikey=demo"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                price = data[0]['price']
                return int(price)
    except Exception:
        pass
    
    try:
        # روش 2: از MarketWatch با ساختار دقیق‌تر
        url = "https://www.marketwatch.com/investing/future/gold"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # چندین روش برای پیدا کردن قیمت
        selectors = [
            'span[class*="value"]',
            'bg-quote[class*="value"]',
            'div[class*="price"]',
            'span[class*="price"]'
        ]
        
        for selector in selectors:
            price_elements = soup.select(selector)
            for element in price_elements:
                price_text = element.text.strip()
                if price_text and any(c.isdigit() for c in price_text):
                    try:
                        price = float(price_text.replace(',', '').replace('$', ''))
                        if 1000 < price < 3000:  # محدوده منطقی قیمت طلا
                            return int(price)
                    except:
                        continue
    except Exception:
        pass
    
    try:
        # روش 3: از Investing.com با ساختار متفاوت
        url = "https://api.investing.com/api/financialdata/tablelist/8830?field=last"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                price = data['data'][0]['last']
                return int(price)
    except Exception:
        pass
    
    # روش 4: از Yahoo Finance برای Gold Futures
    try:
        gold = yf.Ticker("GC=F")
        data = gold.history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            return int(price)
    except Exception:
        pass
    
    return 0  # اگر پیدا نشد، صفر برگردون

# --- تابع اصلی ---
def get_prices():
    prices = {}

    # --- قیمت‌ها از TGJU ---
    try:
        page = requests.get("https://www.tgju.org", timeout=10)
        if page.status_code != 200:
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

    except Exception:
        return None

    # --- انس جهانی طلا ---
    gold_price = get_gold_ounce()
    prices['انس طلا'] = gold_price

    # --- بیت کوین و اتریوم ---
    try:
        btc = yf.Ticker("BTC-USD").history(period="1d")
        prices['بیت کوین'] = int(btc['Close'].iloc[-1]) if not btc.empty else 0
    except Exception:
        prices['بیت کوین'] = 0

    try:
        eth = yf.Ticker("ETH-USD").history(period="1d")
        prices['اتریوم'] = int(eth['Close'].iloc[-1]) if not eth.empty else 0
    except Exception:
        prices['اتریوم'] = 0

    return prices
