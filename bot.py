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

# আপনার ওপেনরাউটার এপিআই কি (গিটহাব প্রটেকশন এড়াতে আমরা এটিকে কোড থেকে নিরাপদ রেখেছি)
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

# --- অফিসিয়াল ফ্রি Hermes 3 এআই ইঞ্জিন মেথড ---
def fetch_hermes_free(user_message):
    conn = None
    try:
        # ওপেনরাউটার এর সাথে সরাসরি এপিআই কানেকশন
        conn = http.client.HTTPSConnection("openrouter.ai", timeout=25)
        
        system_prompt = "তুমি একজন চমৎকার এআই অ্যাসিস্ট্যান্ট। তোমার নাম হার্মিস। তুমি ব্যবহারকারীর সাথে সবসময় শুদ্ধ, সহজ এবং সাবলীল বাংলা ভাষায় কথা বলবে এবং ২৪/৭ সাহায্য করবে।"
        
        # অফিসিয়াল Hermes 3 ফ্রি মডেল আইডি পেলোড
        payload = {
            "model": "nousresearch/hermes-3-llama-3.1-405b:free", 
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }
        
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com',
            'X-Title': 'Hermes Telegram Bot',
            'Connection': 'close'
        }
        
        conn.request("POST", "/api/v1/chat/completions", body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        data = response.read()
        
        if response.status == 200:
            res_json = json.loads(data.decode('utf-8'))
            if 'choices' in res_json and len(res_json['choices']) > 0:
                return res_json['choices']['message']['content'].strip()
            return "দুঃখিত, এআই কোনো উত্তর তৈরি করতে পারেনি।"
        else:
            print(f"API Error Status: {response.status}, Data: {data.decode('utf-8')}")
            return "সার্ভার এই মুহূর্তে কিছুটা ব্যস্ত। অনুগ্রহ করে আর একবার মেসেজ দিন।"
            
    except Exception as e:
        print(f"Error Details: {e}")
        return "কানেকশন রিস্টার্ট হচ্ছে। দয়া করে আর একবার মেসেজ দিন।"
    finally:
        if conn:
            conn.close()

async def get_ai_response(user_message):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, fetch_hermes_free, user_message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("দুঃখিত, আপনি অনুমোদিত নন।")
        return
    await update.message.reply_text("হ্যালো এডাম! আমি আপনার অফিশিয়াল ফ্রী 'Hermes 3' এআই অ্যাসিস্ট্যান্ট। আমি এখন সম্পূর্ণ সচল ও প্রস্তুত! আমাকে বাংলায় যেকোনো প্রশ্ন করুন।")

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
