import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

# ====== НАСТРОЙКИ ======
BOT_TOKEN = "8706687234:AAHkQXqsmx_DezA9SCqqCTEFlPsPEybR8wo"  # Замените на токен вашего бота
OPENAI_API_KEY = "sk-84IfuBfcs_gOu4JlODD1S6BZ4v_etJlQ4qLgj4jJMGUht-Y3P2h9ipKnvN4duGEqCyskmjSMMq5RT-ropFuXjQ"  # Замените на токен ИИ

# ====== ЛОГИРОВАНИЕ ======
logging.basicConfig(level=logging.INFO)

# ====== ИНИЦИАЛИЗАЦИЯ БОТА ======
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ====== ОБРАБОТЧИК /START ======
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "<b><tg-emoji emoji-id=\"5413694143601842851\">👋</tg-emoji> Привет! Я поддержка NodeLink. Напиши мне свои проблемы, вопросы или предложения, и я тебе помогу!</b>",
        parse_mode="HTML"
    )

# ====== ОБРАБОТЧИК ВСЕХ ТЕКСТОВЫХ СООБЩЕНИЙ ======
@dp.message(lambda message: message.text)
async def filter_messages(message: types.Message):
    client = OpenAI(
        base_url="https://api.langdock.com/openai/eu/v1",
        api_key=OPENAI_API_KEY
    )
    processing_msg = await message.reply("<b><tg-emoji emoji-id=\"5350427505805238170\">⏳</tg-emoji> Печатает</b>", parse_mode="HTML")

    completion = client.chat.completions.create(
        model="gpt-5",  # можно оставить "gpt-5" или "gpt-40-mini", если требуется
        messages=[
            {"role": "system", "content": "Ты — дружелюбная поддержка бота NodeLink. Общайся просто, по-дружески и современно, будто с другом. NodeLink — это реферальный бот, который платит за приглашённых друзей и за выполнение заданий. Твоя задача — помогать пользователям, решать их проблемы или направлять в нужные места. Основные правила ответов: 1. Если у пользователя не отображаются Приложение, Магазин, Ивент, Профиль, Задание или Рефералы — скажи обновить страницу через три точки (кнопка «Обновить») или заново зайти в бота через /start. 2. Если заблокировали без причины — успокой, скажи, что скоро всё исправят и модерация свяжется при необходимости. 3. Если просят быстрее вывести товары или коины — скажи, что модераторы уже обрабатывают заказы и нужно чуть подождать. 4. Если хотят стать спонсором или добавить задание — отправь в анкету: [https://replit.com/](https://replit.com/) и напиши это красиво и доброжелательно. 5. Если хотят купить рекламу — тоже отправь в анкету: [https://replit.com/](https://replit.com/) и вежливо объясни. 6. Если ошибка с покупкой или купил не тот товар — напиши, что запрос отправлен в модерацию, и оператор скоро свяжется. Если вопрос не подходит ни под один пункт — отвечай по-дружески, постарайся помочь сам. В крайнем случае скажи, что запрос отправлен, и модератор скоро напишет. Отвечай коротко, ясно и дружелюбно."},
            {"role": "user", "content": message.text}  # текст пользователя
        ]
    )

    await bot.delete_message(message.chat.id, processing_msg.message_id)

    response_text = completion.choices[0].message.content
    await message.answer(response_text, parse_mode="Markdown")

# ====== ЗАПУСК БОТА ======
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
