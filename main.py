import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = "8639268299:AAF8dgiMVPVqK6ILmv8Q2otVByfhMjWmOMg"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# БАЗА ДАННЫХ В ИДЕ КАТАЛОГА (замените примеры на ваши данные)
VIDEO_CATALOG = {
    "video_1": {
        "title": "Даня Серёжа",
        "description": "",
        "price": 13,  # Цена в Telegram Stars
        "file_id": "AAMCAgADGQEAAS-zvWrOFbsJoPcGor0BME75JTZzzZtuAALVngACOtmZSyMR4fONq-MuAQAHbQADPQQ"
    },
    "video_2": {
        "title": "2",
        "description": "",
        "price": 13,  # Цена в Telegram Stars
        "file_id": "AAMCAgADGQEAAS-zwmrOFgdZmvkomXvG7Zp5X8BRDxIIAAIBEwAC3p4ZSd34rtc2e_CyAQAHbQADPQQ"
    }
}

# 1. Главное меню со списком доступных видео
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем удобные кнопки прямо в тексте
    builder = InlineKeyboardBuilder()
    
    # Автоматически добавляем кнопку для каждого видео из нашего каталога
    for video_id, data in VIDEO_CATALOG.items():
        builder.row(types.InlineKeyboardButton(
            text=f"{data['title']} — {data['price']} ⭐️",
            callback_data=f"buy_{video_id}" # Передаем ID видео при нажатии
        ))
        
    await message.answer(
        text="👋 Привет! Добро пожаловать в наш магазин видеороликов.\n\n"
             "Выбери из списка ниже видео, которое хочешь приобрести:",
        reply_markup=builder.as_markup()
    )

# 2. Обработка нажатия на кнопку (выставление счета за конкретное видео)
@dp.callback_query(F.data.startswith("buy_"))
async def process_buy_click(callback: types.CallbackQuery):
    video_id = callback.data.split("_")[1] # Получаем ID (video_1, video_2 и т.д.)
    video_data = VIDEO_CATALOG.get(video_id)
    
    if not video_data:
        await callback.answer("Товар не найден!", show_alert=True)
        return

    # Убираем часы загрузки на кнопке
    await callback.answer()
    
    # Отправляем инвойс на оплату именно этого видео
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=video_data["title"],
        description=video_data["description"],
        payload=video_id,  # Передаем ID видео в систему оплаты, чтобы потом понять, ЧТО именно купили
        provider_token="",  
        currency="XTR",     
        prices=[types.LabeledPrice(label="Покупка", amount=video_data["price"])]
    )

# 3. Подтверждение готовности принять платеж
@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# 4. Выдача нужного видео после успешной оплаты
@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    # Достаем ID видео из payload успешного платежа
    video_id = message.successful_payment.invoice_payload
    video_data = VIDEO_CATALOG.get(video_id)
    
    if video_data:
        await message.answer(f"🎉 Спасибо за покупку фильма «{video_data['title']}»! Приятного просмотра:")
        
        # Отправляем видео с защитой от пересылки
        await bot.send_video(
            chat_id=message.chat.id,
            video=video_data["file_id"],
            protect_content=True
        )
    else:
        await message.answer("Произошла ошибка, но оплата прошла. Напишите в поддержку.")