# - *- coding: utf- 8 - *-
import sqlite3
from pydantic import BaseModel

from bot.data.config import PATH_DATABASE
from bot.database.db_helper import dict_factory, update_format_where, update_format


class DealsModel(BaseModel):
    increment: int
    deal_id: str
    deal_amount: float
    deal_currency: str
    deal_description: str
    deal_status: str
    deal_address: str
    deal_member: int | None
    deal_owner_id: int | None
    deal_payment_method: str
    seller_confirmed: int
    buyer_confirmed: int


class Deals:
    storage_name = "storage_deals"

    @staticmethod
    def add(
        deal_id: str,
        deal_amount: float,
        deal_currency: str,
        deal_description: str,
        deal_address: str,
        deal_owner_id: int,
        deal_payment_method: str,
    ):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            con.execute(
                f"""
                INSERT INTO {Deals.storage_name} (
                    deal_id, deal_amount, deal_currency, deal_description,
                    deal_status, deal_address, deal_member, deal_owner_id,
                    deal_payment_method, seller_confirmed, buyer_confirmed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
                """,
                [
                    deal_id, str(deal_amount), deal_currency, deal_description,
                    "waiting", deal_address, 0, deal_owner_id,
                    deal_payment_method
                ],
            )

    @staticmethod
    def get(**kwargs) -> DealsModel | None:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql, parameters = update_format_where(
                f"SELECT * FROM {Deals.storage_name}", kwargs
            )
            response = con.execute(sql, parameters).fetchone()
            return DealsModel(**response) if response is not None else None

    @staticmethod
    def gets(**kwargs) -> list[DealsModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql, parameters = update_format_where(
                f"SELECT * FROM {Deals.storage_name}", kwargs
            )
            response = con.execute(sql, parameters).fetchall()
            return [DealsModel(**row) for row in response]

    @staticmethod
    def get_all() -> list[DealsModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            response = con.execute(f"SELECT * FROM {Deals.storage_name}").fetchall()
            return [DealsModel(**row) for row in response]

    @staticmethod
    def update(deal_id, **kwargs):
        if not kwargs:
            return
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql, parameters = update_format(f"UPDATE {Deals.storage_name} SET", kwargs)
            parameters.append(deal_id)
            con.execute(sql + " WHERE deal_id = ?", parameters)

    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql, parameters = update_format_where(
                f"DELETE FROM {Deals.storage_name}", kwargs
            )
            con.execute(sql, parameters)

    @staticmethod
    def clear():
        with sqlite3.connect(PATH_DATABASE) as con:
            con.execute(f"DELETE FROM {Deals.storage_name}")
