from aiogram import executor
from handlers import dp
from resourses.middleware import AuthMiddleware


if __name__ == '__main__':
    dp.middleware.setup(AuthMiddleware())
    executor.start_polling(dp)
