from aiogram import executor
from handlers import dp
from resourses.middleware import AuthMiddleware
from resourses.notify_admin import shutdown, startup


if __name__ == '__main__':
    dp.middleware.setup(AuthMiddleware())
    executor.start_polling(dp, on_startup=startup, on_shutdown=shutdown)
