import asyncio
from datetime import datetime
import json
import logging
from os import getenv
import sys
from typing import Any, Dict, Tuple

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


def validate_user_input(user_input: Dict[str, str]) -> bool:
    if not all(
        key in ['dt_from', 'dt_upto', 'group_type'] for key in user_input
    ):
        raise Exception('Отсутствуют необходимые данные.')


def validate_date_string(date: str) -> datetime:
    try:
        return datetime.fromisoformat(date)
    except Exception:
        raise Exception(f'Невалидная дата: {date}')


def validate_group_type(group_type: str) -> str:
    if group_type in ['hour', 'day', 'month', 'year']:
        return group_type
    else:
        raise Exception(
            f'Невалидный идентификатор группировки: {group_type}'
        )


def validate_timeframe(dt_from: datetime, dt_upto: datetime) -> None:
    if dt_from >= dt_upto:
        raise Exception('"dt_from" должно быть меньше "dt_upto"')


def read_user_input(text: str) -> Tuple[datetime, datetime, str]:
    try:
        user_input = json.loads(text)
    except Exception:
        raise Exception('Невалидные данные.')
    validate_user_input(user_input)
    dt_from, dt_upto, group_type = (
        validate_date_string(user_input.get('dt_from')),
        validate_date_string(user_input.get('dt_upto')),
        validate_group_type(user_input.get('group_type'))
    )
    validate_timeframe(dt_from, dt_upto)
    return dt_from, dt_upto, group_type


async def form_report(
        dt_from: datetime, dt_upto: datetime, group_type: str
) -> Any:

    pipeline = [
        {
            "$match": {
                "dt": {
                    "$gte": dt_from,
                    "$lte": dt_upto
                }
            }
        },
        {
            "$densify": {
                "field": "dt",
                "range": {
                    "step": 1,
                    "unit": group_type,
                    "bounds": [dt_from, dt_upto]
                }
            }
        },
        {
            "$project": {
                "value": 1,
                "dt": 1,
                "label": {
                    "$dateToString": {
                        "format": "%Y-%m-%dT%H:%M:%S",
                        "date": {
                            "$dateTrunc": {
                                "date": "$dt", "unit": group_type
                            }
                        }
                    }
                }
            }
        },
        {
            "$group": {
                "_id": "$label",
                "sum": {"$sum": "$value"},
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        }
    ]

    result = [row async for row in collection.aggregate(pipeline)]
    report = {
        "dataset": [row['sum'] for row in result],
        "labels": [row['_id'] for row in result]
    }
    return json.dumps(report, indent=True)


@dp.message()
async def command_aggregate_data(message: Message) -> None:
    try:
        dt_from, dt_upto, group_type = read_user_input(message.text)
        await message.answer(await form_report(
            dt_from, dt_upto, group_type
        ))
    except Exception as error:
        logging.error(error)
        await message.answer(
            'Невалидный запрос. Пример запроса:\n'
            '{"dt_from": "2022-09-01T00:00:00", '
            '"dt_upto": "2022-12-31T23:59:00", '
            '"group_type": "month"}'
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
