import os
import requests

token = os.environ["BOT_TOKEN"]
chat_id = os.environ["CHANNEL_ID"]

text = "سلام از GitHub Actions 🚀"

url = f"https://api.telegram.org/bot{token}/sendMessage"
r = requests.post(url, data={"chat_id": chat_id, "text": text})

print("Status:", r.status_code)
print("Response:", r.text)
