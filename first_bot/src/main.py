import logging
import uuid
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import aiohttp 

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

    async with aiohttp.ClientSession() as session:
        try:
            async def fetch():
                async with session.post(OPENROUTER_URL, headers=headers, json=data) as response:
                    response.raise_for_status()  
                    return await response.json()
            result = await fetch()
            return result['choices'][0]['message']['content']
        except aiohttp.ClientError as e:
            print(f"Ошибка запроса к OpenRouter API: {e}")
            return "Произошла ошибка при взаимодествии с языковой моделью."
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            return "Произошла непредвиденная ошибка. Бебебе"


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

    await message.answer(
        llm_response
    )
    logger.info("Ответ отправлен пользователю %s", user_id)

if __name__ == '__main__':
    print("Бот запущен. Жду сообщений...")
    dp.run_polling(bot, skip_updates=True)