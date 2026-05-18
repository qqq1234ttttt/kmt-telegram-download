import os
import telebot
import yt_dlp
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ---------- Video Download Logic ----------
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

# ---------- Flask Webhook Routes ----------
@app.route('/')
def index():
    return "Bot is running (Webhook mode)"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Unsupported Media Type", 415

# ---------- Main Entry Point ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Webhook ကို ဒီမှာ အလိုအလျောက် set မလုပ်ဘဲ Render ပေါ်တင်ပြီးမှ တစ်ကြိမ် terminal ကနေ run ပါ
    app.run(host="0.0.0.0", port=port)
