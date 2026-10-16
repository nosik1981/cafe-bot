import asyncio
import os
from aiohttp import web
from bot import dp, bot


async def handle_root(request):
    return web.Response(text="Cafe bot is running")


async def handle_health(request):
    return web.Response(text="OK")


async def on_startup(app):
    # Запускаем polling бота в фоне
    asyncio.create_task(dp.start_polling(bot))
    print("Bot polling started")


async def on_shutdown(app):
    await bot.session.close()


def main():
    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_get("/health", handle_health)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
