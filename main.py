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
    'channel link', 'group link', 'share karo', 'forward karo',
    'paribook', 'id banao', 'hojao', 'lifetime', 'safest platform',
    'pe id', 'create id', 'register', 'sign up', 'telegram pe',
]

# Betting odds patterns to skip (not actual scores)
betting_patterns = [
    r'\d+\s+ka\s+\d+',          # "67 KA 90/11"
    r'\d+-\d+\s+\d+\s+over',    # "57-8 6 OVER"
    r'\d+\s+balls\s+\d+\s+runs\s+reqd',  # "84 BALLS 204 RUNS REQD"
    r'runs\s+reqd',              # "RUNS REQD"
    r'reqd\s+per\s+over',        # "REQD PER OVER"
    r'\d+\s+years\s+in\s+ipl',   # "2 YEARS IN IPL"
]

score_keywords = [
    'over', 'ball', 'wide', 'no ball', 'dot', 'bye',
    'six', 'sixx', 'four', 'fourr', 'boundary', 'on strike',
    'wkt', 'wicket', 'out', 'bowled', 'caught', 'lbw', 'runout',
    'run rate', 'scorecard', 'ipl', 't20', 'odi',
    'mumbai', 'chennai', 'bangalore', 'kolkata', 'delhi',
    'hyderabad', 'rajasthan', 'punjab', 'lucknow', 'gujarat',
    'india', 'pakistan', 'australia', 'england',
    'last ball', 'current run rate',
]

score_patterns = [
    r'\d{1,3}\/\d',
    r'\d{1,2}\.\d\s+\d+\/\d',
    r'\d+\s+over\s+\d+\/\d',
]

def is_spam(text):
    lower = text.lower()
    return any(word in lower for word in spam_keywords)

def is_betting_odds(text):
    lower = text.lower()
    return any(re.search(p, lower) for p in betting_patterns)

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
        print(f"📤 Server response: {res.status_code}", flush=True)
    except Exception as e:
        print(f"Server send error: {e}", flush=True)

async def main():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

    @client.on(events.NewMessage(chats=SOURCE_CHANNEL_ID))
    async def handle_message(event):
        text = event.message.text or ""
        if not text:
            return
        if is_spam(text):
            print(f"❌ Spam skipped: {text[:60]}", flush=True)
            return
        if is_betting_odds(text):
            print(f"⚡ Betting odds skipped: {text[:60]}", flush=True)
            return
        if is_score(text):
            print(f"✅ Score: {text[:80]}", flush=True)
            send_to_server(text)
            try:
                await client.forward_messages(DEST_CHANNEL_ID, event.message)
                print("📨 Forwarded to private channel", flush=True)
            except Exception as e:
                print(f"Forward error: {e}", flush=True)

    await client.start()
    print("🚀 Forwarder started!", flush=True)
    print("✅ Telethon connected successfully!", flush=True)
    print(f"📡 Listening to channel: {SOURCE_CHANNEL_ID}", flush=True)
    await client.run_until_disconnected()

asyncio.run(main())
