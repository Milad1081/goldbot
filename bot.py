import os, requests

token = os.environ["BOT_TOKEN"]
chat_id = os.environ["CHANNEL_ID"]

url = f"https://api.telegram.org/bot{token}/sendMessage"
r = requests.post(url, data={"chat_id": chat_id, "text": "سلام از GitHub Actions 🚀"})

print("Status:", r.status_code)
print("Response:", r.text)
