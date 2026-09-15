# - *- coding: utf- 8 - *-
import sqlite3
from pydantic import BaseModel

from bot.data.config import PATH_DATABASE
from bot.database.db_helper import dict_factory, update_format_where, update_format
from bot.utils.const_functions import get_unix


class BanModel(BaseModel):
    increment: int
    user_id: int
    user_login: str
    reason: str
    banned_by: int
    ban_unix: int


class Banx:
    storage_name = "storage_bans"

    @staticmethod
    def add(user_id: int, user_login: str, reason: str, banned_by: int):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            # Если уже есть — обновим причину
            existing = con.execute(
                f"SELECT * FROM {Banx.storage_name} WHERE user_id = ?",
                [user_id],
            ).fetchone()
            if existing:
                con.execute(
                    f"UPDATE {Banx.storage_name} SET reason = ?, banned_by = ?, ban_unix = ?, user_login = ? WHERE user_id = ?",
                    [reason, banned_by, get_unix(), user_login.lower(), user_id],
                )
            else:
                con.execute(
                    f"""
                    INSERT INTO {Banx.storage_name} (
                        user_id, user_login, reason, banned_by, ban_unix
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    [user_id, user_login.lower(), reason, banned_by, get_unix()],
                )

    @staticmethod
    def get(**kwargs) -> BanModel | None:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql, parameters = update_format_where(
                f"SELECT * FROM {Banx.storage_name}", kwargs
            )
            response = con.execute(sql, parameters).fetchone()
            return BanModel(**response) if response is not None else None

    @staticmethod
    def get_all() -> list[BanModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            response = con.execute(
                f"SELECT * FROM {Banx.storage_name} ORDER BY ban_unix DESC"
            ).fetchall()
            return [BanModel(**row) for row in response]

    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql, parameters = update_format_where(
                f"DELETE FROM {Banx.storage_name}", kwargs
            )
            con.execute(sql, parameters)

    @staticmethod
    def is_banned(user_id: int) -> BanModel | None:
        return Banx.get(user_id=user_id)
