import asyncio
import logging
from os import getenv, environ
from dotenv import load_dotenv

import django

environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()
from commands import private
from aiogram import Dispatcher, Bot
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from main.tg_bot.admin_private import admin_private
from main.tg_bot.user_private import user_private
from main.tg_bot.track_orders import notify_user

load_dotenv()

bot = Bot(getenv('bot_token'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def start_bot():
    dp.include_routers(user_private, admin_private)
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def start_tracking_orders():
    while True:
        await asyncio.sleep(20)
        try:
            await notify_user(bot)
        except Exception as err:
            print(f"{type(err)} - {err}")


def finish_all_tasks(tasks):
    for task in tasks:
        if not task.done():
            task.cancel()


async def main():
    tasks = [
        asyncio.create_task(start_bot()),
        asyncio.create_task(start_tracking_orders()),
    ]

    tasks[0].add_done_callback(lambda x: finish_all_tasks(tasks))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Завершение работы')
