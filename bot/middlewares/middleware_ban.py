# - *- coding: utf- 8 - *-
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from bot.data.config import get_admins
from bot.database.db_bans import Banx
from bot.utils.const_functions import ded


class BanMiddleware(BaseMiddleware):
    """Блокирует забаненных пользователей: уведомляет о бане и причине."""

    async def __call__(self, handler, event: TelegramObject, data: dict):
        user = data.get("event_from_user")
        if user is None or user.is_bot:
            return await handler(event, data)

        # Админы не блокируются
        if user.id in get_admins():
            return await handler(event, data)

        ban = Banx.is_banned(user.id)
        if ban is None:
            return await handler(event, data)

        text = ded(f"""
            🚫 <b>Вы заблокированы в этом боте.</b>

            📌 <b>Причина:</b> {ban.reason}
        """)

        try:
            if isinstance(event, Message):
                await event.answer(text)
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Вы заблокированы в этом боте.", show_alert=True)
                try:
                    await event.message.answer(text)
                except Exception:
                    pass
        except Exception:
            pass

        # Не передаём дальше в хендлеры
        return None
