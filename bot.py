import logging
import os
import requests
import threading
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

# --- সম্পূর্ণ ফ্রি ও সরাসরি এআই প্রোভাইডার (কোনো API Key লাগবে না) ---
def get_ai_response(user_message):
    try:
        # বিশ্বের অন্যতম বিখ্যাত ফ্রি টেস্ট গেটওয়ে (Pollinations AI) ব্যবহার করছি যা সর্বদা সচল থাকে
        system_prompt = "তুমি একজন চমৎকার এআই অ্যাসিস্ট্যান্ট। তোমার নাম হার্মিস। তুমি ব্যবহারকারীর সাথে সবসময় শুদ্ধ, সহজ এবং সাবলীল বাংলা ভাষায় কথা বলবে এবং ২৪/৭ সাহায্য করবে।"
        
        # URL এ সঠিকভাবে প্রম্পট পাঠানোর জন্য ফরম্যাটিং
        url = f"https://pollinations.ai{requests.utils.quote(user_message)}?system={requests.utils.quote(system_prompt)}&model=openai"
        
        response = requests.get(url, timeout=20)
        
        if response.status_code == 200 and response.text:
            return response.text.strip()
        else:
            return "দুঃখিত, এআই প্রসেসিংয়ে কিছুটা সমস্যা হয়েছে। দয়া করে আবার চেষ্টা করুন।"
            
    except Exception as e:
        print(f"Error Details: {e}")
        return "কানেকশন সাময়িকভাবে ব্যাহত হয়েছে। অনুগ্রহ করে আর একবার মেসেজ দিন।"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("দুঃখিত, আপনি অনুমোদিত নন।")
        return
    await update.message.reply_text("হ্যালো! আমি আপনার ২৪/৭ হার্মিস এআই এজেন্ট। কোনো এপিআই কি ছাড়াই আমি এখন সম্পূর্ণ অ্যাক্টিভ! আমাকে বাংলায় যেকোনো প্রশ্ন করুন।")

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
