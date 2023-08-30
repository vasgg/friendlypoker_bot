from aiogram import Dispatcher
from config import admin, logger


async def startup(dp: Dispatcher) -> None:
    await dp.bot.send_message(admin, 'Bot started')
    logger.info("bot started")


async def shutdown(dp: Dispatcher) -> None:
    await dp.bot.send_message(admin, 'Bot shutdown')
    logger.info("Bot shutdown")
