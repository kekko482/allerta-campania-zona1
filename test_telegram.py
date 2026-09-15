import os
import urllib.request
import urllib.parse

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = "5891919449"

message = """🤖 TEST BOT PROTEZIONE CIVILE

Il collegamento Telegram funziona correttamente! ✅

📍 Zona monitorata: Zona 1
🌧️ Sistema: Allerta Campania
"""

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

data = urllib.parse.urlencode({
    "chat_id": CHAT_ID,
    "text": message
}).encode()

request = urllib.request.Request(url, data=data)

with urllib.request.urlopen(request) as response:
    print(response.read().decode())
