import logging
import os
import threading
import http.client
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- আপনার টেলিগ্রাম কনফিগারেশন ---
TELEGRAM_BOT_TOKEN = "8272479437:AAHqq3ny4Ng2p3PVvWQUafwp78Xinrmv3MM"
ALLOWED_USER_ID = 8523238784  

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

# --- সরাসরি পাইথন কোর কানেকশন দিয়ে ফ্রি এআই গেটওয়ে ---
def get_ai_response(user_message):
    try:
        # নেটওয়ার্ক ব্লক এড়াতে পাইথনের নিজস্ব কোর কানেকশন মেথড
        conn = http.client.HTTPSConnection("text.pollinations.ai")
        system_prompt = "তুমি একজন চমৎকার এআই অ্যাসিস্ট্যান্ট। তোমার নাম হার্মিস। তুমি ব্যবহারকারীর সাথে সবসময় শুদ্ধ, সহজ এবং সাবলীল বাংলা ভাষায় কথা বলবে এবং ২৪/৭ সাহায্য করবে।"
        
        # URL সেফ এনকোডিং
        encoded_msg = urllib.parse.quote(user_message)
        encoded_sys = urllib.parse.quote(system_prompt)
        
        path = f"/{encoded_msg}?system={encoded_sys}&model=openai"
        
        # ব্রাউজার ট্রাফিক ইমুলেট করার জন্য কাস্টম হেডার্স
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*'
        }
        
        conn.request("GET", path, headers=headers)
        response = conn.getresponse()
        data = response.read()
        
        if response.status == 200:
            return data.decode('utf-8').strip()
        else:
            return "দুঃখিত, আমি আপনার মেসেজটি বুঝতে পেরেছি কিন্তু সার্ভার প্রসেস করতে পারছে না। দয়া করে আবার পাঠান।"
            
    except Exception as e:
        print(f"Error Details: {e}")
        return "সার্ভার এই মুহূর্তে একটু রিফ্রেশ হচ্ছে। অনুগ্রহ করে আর একবার মেসেজ দিন।"

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
    ai_reply = get_ai_response(update.message.text)
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
