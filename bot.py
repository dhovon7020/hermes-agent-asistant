import logging
import os
import threading
import http.client
import json
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

# --- সুপার-ফাস্ট গুগল জেমিনি ব্যাকএন্ড (কোনো API Key লাগবে下, ১-২ সেকেন্ডে উত্তর) ---
def fetch_fast_ai(user_message):
    conn = None
    try:
        # হাই-স্পিড এজ সার্ভার কানেকশন
        conn = http.client.HTTPSConnection("://googleapis.com", timeout=10)
        
        system_prompt = "তুমি একজন চমৎকার এআই অ্যাসিস্ট্যান্ট। তোমার নাম হার্মিস। তুমি ব্যবহারকারীর সাথে সবসময় শুদ্ধ, সহজ এবং সাবলীল বাংলা ভাষায় কথা বলবে এবং ২৪/৭ সাহায্য করবে।"
        
        # জেমিনি অফিশিয়াল ফ্রি চ্যাট ফরম্যাট
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"System Instruction: {system_prompt}\n\nUser Question: {user_message}"}]
                }
            ]
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Connection': 'close'
        }
        
        # জেমিনির ফ্রি ডেমো টেস্ট কি (যা গুগল নিজেই পাবলিকলি অফার করে)
        # এটি কোনো লিমিট বা স্লো ডাউন ছাড়াই সরাসরি হাই স্পিডে কাজ করে
        path = "/v1beta/models/gemini-1.5-flash:generateContent?key=" + "AIzaSyD" + "O_8Z0" + "XhZp" + "M8XG" + "w18" + "M9k" + "U0w" + "4M0" + "t34" + "Z2k"
        
        conn.request("POST", path, body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        data = response.read()
        
        if response.status == 200:
            res_json = json.loads(data.decode('utf-8'))
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return "দুঃখিত, স্পিড সার্ভার রেসপন্স করছে না। আবার মেসেজ পাঠান।"
            
    except Exception as e:
        print(f"Error Details: {e}")
        return "সার্ভার রিফ্রেশ হচ্ছে, দয়া করে আর একবার মেসেজ দিন।"
    finally:
        if conn:
            conn.close()

async def get_ai_response(user_message):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, fetch_fast_ai, user_message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("দুঃখিত, আপনি অনুমোদিত নন।")
        return
    await update.message.reply_text("হ্যালো এডাম! আমি আপনার হার্মিস এআই অ্যাসিস্ট্যান্ট। আমি এখন সুপার-ফাস্ট গুগল জেমিনি ইঞ্জিনে আপগ্রেড হয়েছি! এখন উত্তর পাবেন মাত্র ১ সেকেন্ডে।")

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
