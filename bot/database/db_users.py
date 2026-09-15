# - *- coding: utf- 8 - *-
import sqlite3
from pydantic import BaseModel

from bot.data.config import PATH_DATABASE
from bot.database.db_helper import dict_factory, update_format_where, update_format
from bot.utils.const_functions import get_unix, ded


class UserModel(BaseModel):
    increment: int
    user_id: int
    user_login: str
    user_name: str
    refferal_count: int
    sucessful_deals: int
    user_ton_wallet: str | None
    user_card_wallet: str | None
    user_stars_wallet: str | None
    user_yoomoney_wallet: str | None
    user_unix: int


class Userx:
    storage_name = "storage_users"

    @staticmethod
    def add(user_id: int, user_login: str, user_name: str):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            con.execute(
                ded(f"""
                    INSERT INTO {Userx.storage_name} (
                        user_id, user_login, user_name, refferal_count,
                        sucessful_deals, user_ton_wallet, user_card_wallet,
                        user_stars_wallet, user_yoomoney_wallet, user_unix
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """),
                [user_id, user_login, user_name, 0, 0, None, None, None, None, get_unix()],
            )

    @staticmethod
    def get(**kwargs) -> UserModel | None:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql, parameters = update_format_where(
                f"SELECT * FROM {Userx.storage_name}", kwargs
            )
            response = con.execute(sql, parameters).fetchone()
            return UserModel(**response) if response is not None else None

    @staticmethod
    def gets(**kwargs) -> list[UserModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql, parameters = update_format_where(
                f"SELECT * FROM {Userx.storage_name}", kwargs
            )
            response = con.execute(sql, parameters).fetchall()
            return [UserModel(**row) for row in response]

    @staticmethod
    def get_all() -> list[UserModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            response = con.execute(f"SELECT * FROM {Userx.storage_name}").fetchall()
            return [UserModel(**row) for row in response]

    @staticmethod
    def update(user_id, **kwargs):
        if not kwargs:
            return
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql, parameters = update_format(f"UPDATE {Userx.storage_name} SET", kwargs)
            parameters.append(user_id)
            con.execute(sql + " WHERE user_id = ?", parameters)

    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql, parameters = update_format_where(
                f"DELETE FROM {Userx.storage_name}", kwargs
            )
            con.execute(sql, parameters)

    @staticmethod
    def clear():
        with sqlite3.connect(PATH_DATABASE) as con:
            con.execute(f"DELETE FROM {Userx.storage_name}")
