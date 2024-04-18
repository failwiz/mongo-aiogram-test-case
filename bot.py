import asyncio
import logging
from os import getenv
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from motor import motor_asyncio


client = motor_asyncio.AsyncIOMotorClient("localhost", 27017)
db = client.sampleDB
collection = db.sample_collection


load_dotenv()

TOKEN = getenv('BOT_TOKEN')

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Приветствие на команду /start."""
    await message.answer(
        f'Привет, {html.bold(message.from_user.full_name)}!'
    )


async def main() -> None:
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())