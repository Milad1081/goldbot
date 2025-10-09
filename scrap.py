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
    """دریافت قیمت انس طلا از GoldPriceZ.com"""
    try:
        url = "https://goldpricez.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # پیدا کردن قیمت طلا
        price_element = soup.find('span', class_='display_rates_bid')
        if price_element:
            price_text = price_element.text.strip()
            # حذف $ و فضاهای خالی و تبدیل به عدد
            price = float(price_text.replace('$', '').replace(',', '').strip())
            return int(price)
        
    except Exception as e:
        print(f"GoldPriceZ error: {e}")
    
    return 0

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

    # --- انس جهانی طلا از GoldPriceZ.com ---
    prices['انس طلا'] = get_gold_ounce()

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
