import logging
import os
import requests
import threading
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- আপনার টেলিগ্রাম কনফিগারেশন ---
TELEGRAM_BOT_TOKEN = "8272479437:AAHqq3ny4Ng2p3PVvWQUafwp78Xinrmv3MM"
ALLOWED_USER_ID = 8523238784  

# কোড থেকে এপিআই কি সম্পূর্ণ ডিলিট করা হয়েছে। এটি সিস্টেম মেমোরি থেকে রিড করবে।
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ২৪/৭ সচল রাখার ওয়েব সার্ভার ---
class KeepAliveServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"I am alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), KeepAliveServer)
    print(f"Web Server active on port {port}")
    server.serve_forever()

# --- অফিশিয়াল এবং স্টেবল এআই ইঞ্জিন ---
def fetch_ai_response(user_message):
    if not OPENROUTER_API_KEY:
        return "ভুল: মেমোরিতে OpenRouter API Key খুঁজে পাওয়া যায়নি। দয়া করে কমান্ডটি আবার রান করুন।"

    url = "https://openrouter.ai"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "Hermes Telegram Bot"
    }
    
    # গুগলের অফিশিয়াল এবং অত্যন্ত ফাস্ট ফ্রি মডেল cluster
    payload = {
        "model": "google/gemini-2.5-flash:free",
        "messages": [
            {
                "role": "system", 
                "content": "তুমি একজন চমৎকার এআই অ্যাসিস্ট্যান্ট। তোমার নাম হার্মিস। তুমি ব্যবহারকারীর সাথে সবসময় শুদ্ধ, সহজ এবং সাবলীল বাংলা ভাষায় কথা বলবে এবং ২৪/৭ সাহায্য করবে।"
            },
            {
                "role": "user", 
                "content": user_message
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response_json = response.json()
        
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices']['message']['content'].strip()
        else:
            return "দুঃখিত, গুগল এআই রেসপন্স করতে পারছে না। দয়া করে আবার চেষ্টা করুন।"
            
    except Exception as e:
        return "কানেকশন এরর হয়েছে। দয়া করে আর একবার মেসেজ দিন।"

async def get_ai_response(user_message):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, fetch_ai_response, user_message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("দুঃখিত, আপনি অনুমোদিত নন।")
        return
    await update.message.reply_text("হ্যালো এডাম! আমি আপনার হার্মিস এআই অ্যাসিস্ট্যান্ট। আমি এখন সম্পূর্ণ নতুন ফ্রেমওয়ার্কের সাথে ১০০% সচল আছি! আমাকে বাংলায় যেকোনো প্রশ্ন করুন।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("দুঃখিত, আপনি অনুমোদিত নন।")
        return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    ai_reply = await get_ai_response(update.message.text)
    await update.message.reply_text(ai_reply)

def main():
    threading.Thread(target=run_web_server, daemon=True).start()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("হার্মিস বটটি সফলভাবে চালু হয়েছে...")
    app.run_polling()

if __name__ == '__main__':
    main()
