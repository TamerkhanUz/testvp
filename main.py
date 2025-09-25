from flask import Flask
from aiogram import Bot, Dispatcher, executor, types
import asyncio
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Render 24/7 bot ishlayapti!"

# Telegram bot
API_TOKEN = "BOT_TOKENINGIZ"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.reply("Salom! Render Free bot 🚀")

def run_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
