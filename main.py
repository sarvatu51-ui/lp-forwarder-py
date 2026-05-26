import os
import re
import asyncio
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
SOURCE_CHANNEL_ID = int(os.environ.get("SOURCE_CHANNEL_ID", "-1001736810240"))
DEST_CHANNEL_ID = int(os.environ.get("DEST_CHANNEL_ID", "-1003961918227"))
SERVER_URL = os.environ.get("SERVER_URL", "https://livepointprediction.onrender.com")
BOT_SECRET = os.environ.get("BOT_SECRET", "lpscore2025secret")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Forwarder running!')
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, format, *args):
        pass
        
def run_http():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=run_http, daemon=True).start()

spam_keywords = [
    'join', 'follow', 'subscribe', 'click', 'http', 'www', 't.me',
    'whatsapp', 'instagram', 'youtube', 'facebook',
    'premium', 'paid', 'free offer', 'earn', 'profit',
    'sure shot', 'guaranteed', 'contact us', 'dm us',
    'channel link', 'group link', 'share karo', 'forward karo'
]

score_keywords = [
    'over', 'ball', 'wide', 'no ball', 'dot', 'bye',
    'six', 'sixx', 'four', 'fourr', 'boundary', 'on strike',
    'wkt', 'wicket', 'out', 'bowled', 'caught', 'lbw', 'runout',
    'run rate', 'scorecard', 'ipl', 't20', 'odi',
    'mumbai', 'chennai', 'bangalore', 'kolkata', 'delhi',
    'hyderabad', 'rajasthan', 'punjab', 'lucknow', 'gujarat',
    'india', 'pakistan', 'australia', 'england'
]

score_patterns = [
    r'\d{1,3}\/\d',
    r'\d{1,2}\.\d\s+\d+\/\d',
    r'\d+\s+over',
]

def is_spam(text):
    lower = text.lower()
    return any(word in lower for word in spam_keywords)

def is_score(text):
    lower = text.lower()
    for pattern in score_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return any(word in lower for word in score_keywords)

def send_to_server(text):
    try:
        res = requests.post(
            f"{SERVER_URL}/api/activematch/livescore",
            json={"text": text},
            headers={"x-bot-secret": BOT_SECRET},
            timeout=5
        )
        print(f"📤 Server response: {res.status_code}")
    except Exception as e:
        print(f"Server send error: {e}")

async def main():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

    @client.on(events.NewMessage(chats=SOURCE_CHANNEL_ID))
    async def handle_message(event):
        text = event.message.text or ""
        if not text:
            return
        if is_spam(text):
            print(f"❌ Spam skipped: {text[:60]}")
            return
        if is_score(text):
            print(f"✅ Score: {text[:80]}")
            send_to_server(text)
            try:
                await client.forward_messages(DEST_CHANNEL_ID, event.message)
                print("📨 Forwarded to private channel")
            except Exception as e:
                print(f"Forward error: {e}")

    await client.start()
    print("🚀 Forwarder started!")
    print("✅ Telethon connected successfully!")
    print(f"📡 Listening to channel: {SOURCE_CHANNEL_ID}")
    await client.run_until_disconnected()

asyncio.run(main())
