import telebot
import yt_dlp
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text

    if not text:
        bot.reply_to(message, "Video Link ပို့ပေးပါ 🙂")
        return

    supported = [
        "tiktok.com",
        "youtube.com",
        "youtu.be",
        "facebook.com",
        "fb.watch"
    ]

    if not any(site in text for site in supported):
        bot.reply_to(
            message,
            "TikTok / YouTube / Facebook Video Link ပို့ပေးပါ 🙂"
        )
        return

    bot.reply_to(message, "Download လုပ်နေပါတယ်... ⏳")

    ydl_opts = {
        "outtmpl": "video.%(ext)s",
        "format": "mp4",
        "quiet": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, "rb") as f:
            bot.send_video(message.chat.id, f)

        os.remove(filename)

    except Exception as e:
        bot.reply_to(message, f"Download မအောင်မြင်ပါ 😢\n{e}")

# --- Web server for Koyeb / Render ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web():
    port = int(os.getenv("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

print("Bot running...")
bot.infinity_polling()
