import logging
import os
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- আপনার কনফিগারেশন ---
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

# --- ফ্রি এআই উত্তর নেওয়ার ডিরেক্ট ফাংশন (API Key ছাড়া ও স্টেবল) ---
def get_ai_response(user_message):
    try:
        # DuckDuckGo AI এর ফ্রি ওপেন গেটওয়ে ব্যবহার করে Gemini/Llama মডেল কল
        url = "https://herokuapp.com"
        payload = {
            "message": f"তুমি একজন চমৎকার এআই অ্যাসিস্ট্যান্ট। তোমার নাম হার্মিস। তুমি ব্যবহারকারীর সাথে সবসময় শুদ্ধ, সহজ এবং সাবলীল বাংলা ভাষায় কথা বলবে। ব্যবহারকারীর প্রশ্ন: {user_message}",
            "model": "gpt-4o"
        }
        response = requests.post(url, json=payload, timeout=15)
        response_json = response.json()
        
        if 'reply' in response_json:
            return response_json['reply']
        elif 'response' in response_json:
            return response_json['response']
        else:
            return "দুঃখিত, আমি এই মুহূর্তে উত্তরটি প্রসেস করতে পারছি না।"
    except Exception as e:
        print(f"Error Details: {e}")
        return "দুঃখিত, এআই সার্ভার এই মুহূর্তে কিছুটা ব্যস্ত আছে। দয়া করে আবার চেষ্টা করুন।"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("দুঃখিত, আপনি অনুমোদিত নন।")
        return
    await update.message.reply_text("হ্যালো! আমি আপনার ২৪/৭ হার্মিস এআই এজেন্ট। আমি এখন সম্পূর্ণ সচল আছি! আমাকে বাংলায় যেকোনো প্রশ্ন করুন।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("দুঃখিত, আপনি অনুমোদিত নন।")
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    ai_reply = get_ai_response(update.message.text)
    await update.message.reply_text(ai_reply)

def main():
    # ব্যাকগ্রাউন্ডে ওয়েব সার্ভার চালু করা
    threading.Thread(target=run_web_server, daemon=True).start()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("হার্মিস বটটি সফলভাবে চালু হয়েছে...")
    app.run_polling()

if __name__ == '__main__':
    main()
