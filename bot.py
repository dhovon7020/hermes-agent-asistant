import logging
import os
import threading
import http.client
import json
import urllib.parse
import asyncio
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

# --- সম্পূর্ণ ফ্রি ও নেটওয়ার্ক-সেফ ডিরেক্ট ক্লাস্টার (কোনো API Key লাগবে না) ---
def fetch_ai_data(user_message):
    conn = None
    try:
        # কোডস্পেস নেটওয়ার্ক ব্লক এড়াতে সম্পূর্ণ আলাদা ফ্রেশ গেটওয়ে
        conn = http.client.HTTPSConnection("text.pollinations.ai", timeout=15)
        
        system_prompt = "তুমি একজন চমৎকার এআই অ্যাসিস্ট্যান্ট। তোমার নাম হার্মিস। তুমি ব্যবহারকারীর সাথে সবসময় শুদ্ধ, সহজ এবং সাবলীল বাংলা ভাষায় কথা বলবে এবং ২৪/৭ সাহায্য করবে।"
        
        # জেসন ফরম্যাট ব্যবহার করে নিরাপদভাবে ডেটা পাঠানো (যাতে ক্যারেক্টার লিক না হয়)
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "model": "searchgpt", # এটি নেটওয়ার্ক ফ্রেন্ডলি এবং সুপার-ফাস্ট ব্যাকএন্ড
            "jsonMode": False
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Connection': 'close'
        }
        
        conn.request("POST", "/", body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        data = response.read()
        
        if response.status == 200:
            result = data.decode('utf-8').strip()
            if result:
                return result
        return "দুঃখিত, এআই প্রসেস করতে কিছুটা সময় নিচ্ছে। আবার মেসেজ দিন।"
            
    except Exception as e:
        print(f"Internal Details: {e}")
        return "সার্ভার এই মুহূর্তে একটু রিফ্রেশ হচ্ছে। অনুগ্রহ করে আর একবার মেসেজ দিন।"
    finally:
        if conn:
            conn.close()

# --- নন-ব্লকিং ব্যাকগ্রাউন্ড থ্রেড রানার ---
async def get_ai_response(user_message):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, fetch_ai_data, user_message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("দুঃখিত, আপনি অনুমোদিত নন।")
        return
    await update.message.reply_text("হ্যালো এডাম! আমি আপনার হার্মিস এআই অ্যাসিস্ট্যান্ট। কোনো এপিআই কি-এর ঝামেলা ছাড়াই আমি এখন ১০০% নিখুঁতভাবে সচল আছি! আমাকে বাংলায় যেকোনো প্রশ্ন করুন।")

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
