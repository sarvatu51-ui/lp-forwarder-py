import os
import re
import requests
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
SOURCE_CHANNEL_ID = int(os.environ.get("SOURCE_CHANNEL_ID", "-1001736810240"))
DEST_CHANNEL_ID = int(os.environ.get("DEST_CHANNEL_ID", "-1003961918227"))
SERVER_URL = os.environ.get("SERVER_URL", "https://livepointprediction.onrender.com")
BOT_SECRET = os.environ.get("BOT_SECRET", "lpscore2025secret")

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

app = Client("lp_forwarder", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.on_message(filters.chat(SOURCE_CHANNEL_ID))
async def handle_message(client, message):
    text = message.text or message.caption or ""
    if not text:
        return
    if is_spam(text):
        print(f"❌ Spam skipped: {text[:60]}")
        return
    if is_score(text):
        print(f"✅ Score: {text[:80]}")
        send_to_server(text)
        try:
            await client.forward_messages(DEST_CHANNEL_ID, SOURCE_CHANNEL_ID, message.id)
            print("📨 Forwarded to private channel")
        except Exception as e:
            print(f"Forward error: {e}")

print("🚀 Forwarder started!")
app.run()
