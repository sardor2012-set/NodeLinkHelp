import asyncio
import logging
import qrcode
from telethon import TelegramClient, events, errors
from openai import OpenAI

# ===== НАСТРОЙКИ =====
api_id = 38307785  # твой api_id с my.telegram.org
api_hash = "b9ee727922af4471a6b8cf437cae7a93"  # твой api_hash
OPENAI_API_KEY = "sk-84IfuBfcs_gOu4JlODD1S6BZ4v_etJlQ4qLgj4jJMGUht-Y3P2h9ipKnvN4duGEqCyskmjSMMq5RT-ropFuXjQ"

logging.basicConfig(level=logging.INFO)

# ===== ИНИЦИАЛИЗАЦИЯ TELETHON =====
client = TelegramClient("session", api_id, api_hash)

# ===== ИНИЦИАЛИЗАЦИЯ OPENAI (через Langdock) =====
client_ai = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.langdock.com/openai/eu/v1"  # важно!
)

# ===== ФУНКЦИЯ QR + 2FA =====
async def login():
    await client.connect()
    if not await client.is_user_authorized():
        print("Сканируй QR код через Telegram на телефоне!")
        qr_login = await client.qr_login()
        
        # Генерируем QR код
        img = qrcode.make(qr_login.url)
        img.show()

        try:
            await qr_login.wait()
        except errors.SessionPasswordNeededError:
            password = input("Введите пароль 2FA Telegram: ")
            await client.sign_in(password=password)
        print("✅ Вход выполнен!")

# ===== ОБРАБОТКА ЛИЧНЫХ СООБЩЕНИЙ =====
@client.on(events.NewMessage)
async def handler(event):
    if event.is_private:
        user_text = event.text
        logging.info(f"Получено сообщение: {user_text}")

        processing_msg = await event.reply("⏳ Обработка...")

        try:
            completion = client_ai.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "Ты — дружелюбная поддержка бота NodeLink. Общайся просто, по-дружески и современно, будто с другом. NodeLink — это реферальный бот, который платит за приглашённых друзей и за выполнение заданий. Твоя задача — помогать пользователям, решать их проблемы или направлять в нужные места. Основные правила ответов: 1. Если у пользователя не отображаются Приложение, Магазин, Ивент, Профиль, Задание или Рефералы — скажи обновить страницу через три точки (кнопка «Обновить») или заново зайти в бота через /start. 2. Если заблокировали без причины — успокой, скажи, что скоро всё исправят и модерация свяжется при необходимости. 3. Если просят быстрее вывести товары или коины — скажи, что модераторы уже обрабатывают заказы и нужно чуть подождать. 4. Если хотят стать спонсором или добавить задание — отправь в анкету: [https://replit.com/](https://replit.com/) и напиши это красиво и доброжелательно. 5. Если хотят купить рекламу — тоже отправь в анкету: [https://replit.com/](https://replit.com/) и вежливо объясни. 6. Если ошибка с покупкой или купил не тот товар — напиши, что запрос отправлен в модерацию, и оператор скоро свяжется. Если вопрос не подходит ни под один пункт — отвечай по-дружески, постарайся помочь сам. В крайнем случае скажи, что запрос отправлен, и модератор скоро напишет. Отвечай коротко, ясно и дружелюбно."},
                    {"role": "user", "content": user_text}
                ]
            )
            response = completion.choices[0].message.content
        except Exception as e:
            response = f"Ошибка ИИ: {e}"

        await client.delete_messages(event.chat_id, [processing_msg.id])

        await event.reply(response)

# ===== ЗАПУСК =====
async def main():
    await login()
    print("Аккаунт готов и отвечает!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
