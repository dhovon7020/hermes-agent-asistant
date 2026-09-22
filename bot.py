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

# আপনার ওপেনরাউটার এপিআই কি
OPENROUTER_API_KEY = "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"

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

# --- অফিসিয়াল ফ্রি Hermes 3 এআই ইঞ্জিন (স্টেবল রিকোয়েস্ট মেথড) ---
def fetch_hermes_response(user_message):
    url = "https://openrouter.ai"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "Hermes Telegram Bot"
    }
    
    # NousResearch এর অফিসিয়াল ফ্রী Hermes 3 (405B) মডেল আইডি
    payload = {
        "model": "nousresearch/hermes-3-llama-3.1-405b:free",
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
        # রিকোয়েস্টে স্টেবল রিকোয়েস্ট লাইব্রেরি ব্যবহার
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response_json = response.json()
        
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices']['message']['content'].strip()
        else:
            print(f"API Debug Logs: {response_json}")
            return "দুঃখিত, এআই প্রোভাইডার এই মুহূর্তে ফ্রি লাইনে অতিরিক্ত ট্রাফিকের সম্মুখীন হচ্ছে। অনুগ্রহ করে আর একবার মেসেজটি পাঠান।"
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return "কানেকশন সাময়িকভাবে ব্যাহত হয়েছে। অনুগ্রহ করে আর একবার মেসেজ দিন।"

# --- নন-ব্লকিং ব্যাকগ্রাউন্ড থ্রেড রানার ---
async def get_ai_response(user_message):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, fetch_hermes_response, user_message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("দুঃখিত, আপনি অনুমোদিত নন।")
        return
    await update.message.reply_text("হ্যালো এডাম! আমি আপনার অফিশিয়াল ফ্রি 'Hermes 3' এআই অ্যাসিস্ট্যান্ট। আমি এখন সম্পূর্ণ নতুন ফ্রেমওয়ার্কের সাথে ১০০% সচল আছি! আমাকে বাংলায় যেকোনো প্রশ্ন করুন।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("দুঃখিত, আপনি অনুমোদিত নন।")
        return
    
    # বট টাইপিং অ্যানিমেশন দেখাবে
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
