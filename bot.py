import logging
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- কনফিগারেশন ---
OPENROUTER_API_KEY = "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"
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

# --- OpenRouter AI API ---
def get_hermes_response(user_message):
    url = "https://openrouter.ai"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "nousresearch/hermes-3-llama-3-8b", 
        "messages": [
            {"role": "system", "content": "তুমি একজন চমৎকার এআই অ্যাসিস্ট্যান্ট। তোমার নাম হার্মিস। তুমি ব্যবহারকারীর সাথে সবসময় শুদ্ধ, সহজ এবং সাবলীল বাংলা ভাষায় কথা বলবে এবং ২৪/৭ সাহায্য করবে।"},
            {"role": "user", "content": user_message}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices']['message']['content']
    except Exception as e:
        return "দুঃখিত, এই মুহূর্তে আমি কোনো উত্তর তৈরি করতে পারছি না।"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("দুঃখিত, আপনি অনুমোদিত নন।")
        return
    await update.message.reply_text("হ্যালো! আমি আপনার ২৪/৭ হার্মিস এআই এজেন্ট। আমাকে বাংলায় যেকোনো প্রশ্ন করুন।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("দুঃখিত, আপনি অনুমোদিত নন。")
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    ai_reply = get_hermes_response(update.message.text)
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
