import asyncio
import os
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import WebAppInfo

# ===== ТОКЕН =====
TOKEN = "8717355777:AAHk6DqLiCfm8cFm1RXNgIhjbjAqgrdUEi0"
ADMIN_ID = 644250377
WEBAPP_URL = "https://cafe-mini-app-zbok.onrender.com/cafe.html"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== ХРАНИЛИЩЕ ИСТОРИИ ЗАКАЗОВ =====
# {user_id: [{"items": [...], "total": ..., "time": "..."}, ...]}
orders_history = {}


# ===== ГЛАВНОЕ МЕНЮ =====
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🍕 Открыть меню", web_app=WebAppInfo(url=WEBAPP_URL))
    builder.button(text="📋 Мои заказы")
    builder.button(text="📞 Связаться")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# ===== /start =====
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Добро пожаловать в кафе «Демо» ☕\n\n"
        "Здесь вы можете заказать вкусную еду с доставкой.\n\n"
        "Нажмите «🍕 Открыть меню», чтобы выбрать блюда.",
        reply_markup=main_menu()
    )


# ===== МОИ ЗАКАЗЫ =====
@dp.message(F.text == "📋 Мои заказы")
async def orders_handler(message: types.Message):
    user_id = message.from_user.id
    user_orders = orders_history.get(user_id, [])

    if not user_orders:
        await message.answer(
            "📋 У вас пока нет заказов.\n\n"
            "Сделайте первый заказ через кнопку «🍕 Открыть меню»!"
        )
        return

    # Показываем последние 10 заказов
    text = f"📋 <b>Ваши заказы</b> (всего: {len(user_orders)}):\n\n"

    for i, order in enumerate(reversed(user_orders[-10:]), 1):
        text += f"<b>Заказ #{i}</b> — {order['time']}\n"
        for item in order['items']:
            text += f"  • {item['name']} × {item['qty']} = {item['price'] * item['qty']} ₽\n"
        text += f"  💰 Итого: <b>{order['total']} ₽</b>\n\n"

    await message.answer(text, parse_mode="HTML")


# ===== СВЯЗАТЬСЯ =====
@dp.message(F.text == "📞 Связаться")
async def contacts_handler(message: types.Message):
    await message.answer(
        "📞 Связаться с нами:\n\n"
        "☎️ Телефон: +7 700 000 00 00\n"
        "📍 Адрес: ул. Примерная, 1\n"
        "🕐 Работаем: 9:00–21:00"
    )


# ===== ПРИЁМ ЗАКАЗА ИЗ MINI APP =====
@dp.message(F.web_app_data)
async def webapp_data_handler(message: types.Message):
    # Парсим данные из витрины
    try:
        data = json.loads(message.web_app_data.data)
    except Exception as e:
        await message.answer("❌ Ошибка при обработке заказа. Попробуйте ещё раз.")
        return

    items = data.get("items", [])
    total = data.get("total", 0)

    # Формируем список товаров
    order_lines = []
    for item in items:
        line = f"• {item['name']} × {item['qty']} = {item['price'] * item['qty']} ₽"
        order_lines.append(line)

    order_text = "\n".join(order_lines)
    time_now = datetime.now().strftime("%d.%m.%Y %H:%M")

    # ===== Сохраняем в историю пользователя =====
    user_id = message.from_user.id
    if user_id not in orders_history:
        orders_history[user_id] = []

    orders_history[user_id].append({
        "items": items,
        "total": total,
        "time": time_now
    })

    # ===== Сообщение админу =====
    admin_message = (
        f"🔔 <b>НОВЫЙ ЗАКАЗ!</b>\n\n"
        f"👤 Клиент: <b>{message.from_user.full_name}</b>\n"
    )

    if message.from_user.username:
        admin_message += f"🔗 @{message.from_user.username}\n"

    admin_message += (
        f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
        f"📦 <b>Состав заказа:</b>\n"
        f"{order_text}\n\n"
        f"💰 <b>Итого: {total} ₽</b>\n\n"
        f"🕐 Время: {time_now}"
    )

    await bot.send_message(ADMIN_ID, admin_message, parse_mode="HTML")

    # ===== Ответ клиенту =====
    await message.answer(
        f"✅ <b>Ваш заказ принят!</b>\n\n"
        f"📦 Состав:\n{order_text}\n\n"
        f"💰 Итого: <b>{total} ₽</b>\n\n"
        f"💳 Ссылку на оплату мы пришлём вам в течение 5 минут.\n\n"
        f"Спасибо за заказ! ☕",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# ===== ЗАПУСК =====
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


