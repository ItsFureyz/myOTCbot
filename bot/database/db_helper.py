# - *- coding: utf- 8 - *-
import sqlite3

from bot.data.config import PATH_DATABASE
from bot.utils.const_functions import get_unix, ded


def dict_factory(cursor, row) -> dict:
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def update_format(sql: str, parameters: dict) -> tuple[str, list]:
    values = ", ".join(f"{item} = ?" for item in parameters)
    return sql + f" {values}", list(parameters.values())


def update_format_where(sql: str, parameters: dict) -> tuple[str, list]:
    sql += " WHERE "
    sql += " AND ".join(f"{item} = ?" for item in parameters)
    return sql, list(parameters.values())


def _columns(con, table: str) -> set[str]:
    return {row["name"] for row in con.execute(f"PRAGMA table_info({table})").fetchall()}


def create_dbx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory

        # Users
        if not _columns(con, "storage_users"):
            con.execute("""
                CREATE TABLE storage_users(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_login TEXT,
                    user_name TEXT,
                    refferal_count INTEGER DEFAULT 0,
                    sucessful_deals INTEGER DEFAULT 0,
                    user_ton_wallet TEXT,
                    user_card_wallet TEXT,
                    user_stars_wallet TEXT,
                    user_yoomoney_wallet TEXT,
                    user_unix INTEGER
                )
            """)
        else:
            cols = _columns(con, "storage_users")
            if "user_stars_wallet" not in cols:
                con.execute("ALTER TABLE storage_users ADD COLUMN user_stars_wallet TEXT")
            if "user_yoomoney_wallet" not in cols:
                con.execute("ALTER TABLE storage_users ADD COLUMN user_yoomoney_wallet TEXT")

        # Referrals
        if not _columns(con, "storage_referrals"):
            con.execute("""
                CREATE TABLE storage_referrals(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    refferal_id INTEGER,
                    refferal_owner INTEGER,
                    refferal_purchase INTEGER DEFAULT 0,
                    refferal_unix INTEGER
                )
            """)

        # Deals
        if not _columns(con, "storage_deals"):
            con.execute("""
                CREATE TABLE storage_deals(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    deal_id TEXT UNIQUE NOT NULL,
                    deal_amount REAL NOT NULL,
                    deal_currency TEXT NOT NULL DEFAULT "TON",
                    deal_description TEXT NOT NULL,
                    deal_status TEXT NOT NULL DEFAULT "waiting",
                    deal_address TEXT NOT NULL,
                    deal_member INTEGER NOT NULL DEFAULT 0,
                    deal_owner_id INTEGER,
                    deal_payment_method TEXT NOT NULL DEFAULT "ton",
                    seller_confirmed INTEGER NOT NULL DEFAULT 0,
                    buyer_confirmed INTEGER NOT NULL DEFAULT 0
                )
            """)
        else:
            cols = _columns(con, "storage_deals")
            additions = {
                "deal_owner_id": "INTEGER",
                "deal_payment_method": 'TEXT NOT NULL DEFAULT "ton"',
                "seller_confirmed": "INTEGER NOT NULL DEFAULT 0",
                "buyer_confirmed": "INTEGER NOT NULL DEFAULT 0",
            }
            for name, definition in additions.items():
                if name not in cols:
                    con.execute(f"ALTER TABLE storage_deals ADD COLUMN {name} {definition}")

            # Best-effort migration for old deals. New deals always store owner_id
            # explicitly, so wallet changes can no longer change the deal owner.
            con.execute("""
                UPDATE storage_deals
                SET deal_owner_id = (
                    SELECT user_id FROM storage_users u
                    WHERE (u.user_ton_wallet = storage_deals.deal_address
                           AND storage_deals.deal_address IS NOT NULL)
                       OR (u.user_card_wallet = storage_deals.deal_address
                           AND storage_deals.deal_address IS NOT NULL)
                    ORDER BY u.increment ASC
                    LIMIT 1
                )
                WHERE deal_owner_id IS NULL
            """)
            con.execute("""
                UPDATE storage_deals
                SET deal_payment_method = CASE
                    WHEN deal_currency IN ('XTR', 'Stars', 'STARS') THEN 'stars'
                    WHEN deal_currency = 'TON' THEN 'ton'
                    ELSE 'card'
                END
                WHERE deal_payment_method IS NULL OR deal_payment_method = ''
            """)

        # Workers
        if not _columns(con, "storage_workers"):
            con.execute("""
                CREATE TABLE storage_workers(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    worker_id INTEGER NOT NULL,
                    worker_deals_sucessful INTEGER DEFAULT 0,
                    worker_deals_cancel INTEGER DEFAULT 0,
                    worker_prefix TEXT NOT NULL,
                    worker_set_unix INTEGER DEFAULT 0
                )
            """)

        print("Database checked/updated.")

        # Bans
        if not _columns(con, "storage_bans"):
            con.execute("""
                CREATE TABLE storage_bans(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    user_login TEXT,
                    reason TEXT NOT NULL,
                    banned_by INTEGER NOT NULL,
                    ban_unix INTEGER NOT NULL
                )
            """)

