import logging
import uuid
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"/usr/src/app/log/bot_{uuid.uuid4().hex[:6]}.log"),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)
logger.info("Логирование настроено. Логи пишутся в %s", f"/usr/src/app/log/bot_{uuid.uuid4().hex[:6]}.log")

API_TOKEN = Path("./test_bot.bot_token").read_text().strip() 
API_KEY = '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'  
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "qwen/qwen3-14b:free" 
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
user_contexts = {}

async def send_to_llm(messages: list) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://t.me/@SerDud_bot",  
        "X-Title": "Telegram Bot"  
    }

    data = {
        "model": OPENROUTER_MODEL,
        "messages": messages
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"


@dp.message(Command("start"))
async def command_start(message: Message):
    logging.info(f"Start msg received. {message.chat.id}")
    user_id = message.from_user.id
    user_contexts[user_id] = []  
    await message.answer("Привет! Я бот с нейросетью. Задай любой вопрос и я на него отвечу.")

@dp.message(Command("help"))
async def command_help(message: Message):
    logging.info(f"Help msg received. {message.chat.id}")
    await message.answer("Мои команды:\n/start - Начать работу с ботом\n/help - Получить справку")


@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    user_message = message.text
    logger.info("Сообщение от %s: %s", user_id, user_message)

    if user_id not in user_contexts:
        user_contexts[user_id] = []
    
    user_contexts[user_id].append({"role": "user", "content": user_message})

    await message.answer("Думаю над ответом...")
    llm_response = await send_to_llm(user_contexts[user_id])
    
    user_contexts[user_id].append({"role": "assistant", "content": llm_response})

    await message.answer(llm_response)
    logger.info("Ответ отправлен пользователю %s", user_id)

if __name__ == '__main__':
    print("Бот запущен. Жду сообщений...")
    dp.run_polling(bot, skip_updates=True)