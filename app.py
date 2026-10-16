import os
import asyncio
from flask import Flask
from bot import dp, bot
import threading

app = Flask(__name__)


@app.route('/')
def index():
    return "Cafe bot is running"


@app.route('/health')
def health():
    return "OK"


def run_bot():
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)