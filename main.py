import asyncio
import os
import dotenv

dotenv.load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.handlers.callback.sms import router as sms_cb_router

from bot.handlers.messages.sms import router as sms_router
from bot.handlers.messages.sessions import router as sessions_router
from bot.handlers.messages.gologin import router as gologin_router
from bot.handlers.messages.proxy import router as proxy_router
from bot.handlers.messages.statistics import router as stats_router
from bot.handlers.messages.credentials import router as credentials_router

from container import BotInstanceContainer


async def main():
    dp = Dispatcher()

    bot = Bot(
        token=os.environ.get("BOT_TOKEN"),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    BotInstanceContainer(bot=bot)

    dp.include_routers(sessions_router)
    dp.include_routers(sms_router)
    dp.include_routers(gologin_router)
    dp.include_routers(proxy_router)
    dp.include_routers(stats_router)
    dp.include_routers(credentials_router)
    dp.include_routers(sms_cb_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
