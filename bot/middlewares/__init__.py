# - *- coding: utf- 8 - *-
from aiogram import Dispatcher

from bot.middlewares.middleware_users import ExistsUserMiddleware
from bot.middlewares.middleware_ban import BanMiddleware


# Регистрация всех миддлварей
def register_all_middlwares(dp: Dispatcher):
    dp.callback_query.outer_middleware(ExistsUserMiddleware())
    dp.message.outer_middleware(ExistsUserMiddleware())
    # Бан после регистрации пользователя, чтобы Userx уже был
    dp.callback_query.middleware(BanMiddleware())
    dp.message.middleware(BanMiddleware())
