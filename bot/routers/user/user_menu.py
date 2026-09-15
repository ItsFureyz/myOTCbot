from typing import Union
# - *- coding: utf- 8 - *-
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram_i18n import I18nContext
from aiogram_i18n.types import InputMediaPhoto
import re

from bot.data.config import GROUP_ID, TOPIC_ID
from bot.database import Userx
from bot.keyboard.inline_user import select_language, back_menu, select_wallet_method
from bot.routers.main_start import show_home_menu
from bot.utils.const_functions import ded, validate_card, validate_yoomoney, send_admins
from bot.utils.misc.bot_models import FSM, ARS

router = Router(name=__name__)


@router.callback_query(F.data == "change_language")
async def choose_language(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    await call.message.reply(
        ded("""
            🌍 Choose your language:
            
            Выберите язык:
        """),
        reply_markup=select_language()
    )


@router.callback_query(F.data == "wallet_add")
async def wallet_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    await call.message.edit_caption(
        caption=i18n.get("select_payment_method"),
        reply_markup=select_wallet_method(i18n)
    )


@router.callback_query(F.data == "card-wallet")
async def wallet_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    user = Userx.get(user_id=call.from_user.id)

    await call.message.edit_caption(
        caption=i18n.get("add-wallet-card-not-exists") if user.user_card_wallet is None else i18n.get(
            "add-wallet-card-exists", wallet=user.user_card_wallet),
        reply_markup=back_menu(i18n)
    )

    await state.set_state("set_cardwallet")


@router.callback_query(F.data == "ton-wallet")
async def wallet_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    user = Userx.get(user_id=call.from_user.id)

    await call.message.edit_caption(
        caption=i18n.get("add-wallet-ton-not-exists") if user.user_ton_wallet is None else i18n.get(
            "add-wallet-ton-exists", wallet=user.user_ton_wallet),
        reply_markup=back_menu(i18n)
    )

    await state.set_state("set_tonwallet")


@router.message(F.text, StateFilter("set_tonwallet"))
async def set_ton_wallet(call: CallbackQuery, bot: Bot, state: FSM, i18n: I18nContext):
    message: str = call.text
    await state.clear()

    if len(message) < 34:
        await call.reply(i18n.get("incorrect_ton_wallet"))
        await state.set_state("set_tonwallet")
        return

    Userx.update(call.from_user.id, user_ton_wallet=message)

    await call.reply(i18n.get("successful_wallet"), reply_markup=back_menu(i18n))




@router.callback_query(F.data == "stars-wallet")
async def stars_wallet_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()
    user = Userx.get(user_id=call.from_user.id)

    await call.message.edit_caption(
        caption=i18n.get(
            "add-wallet-stars-exists",
            wallet=user.user_stars_wallet
        ) if user.user_stars_wallet is not None else i18n.get("add-wallet-stars-not-exists"),
        reply_markup=back_menu(i18n)
    )
    await state.set_state("set_starswallet")


@router.message(F.text, StateFilter("set_starswallet"))
async def set_stars_wallet(message: Message, bot: Bot, state: FSM, i18n: I18nContext):
    username = message.text.strip().lstrip("@")
    await state.clear()

    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{4,31}", username):
        await message.reply(i18n.get("incorrect_stars_wallet"))
        await state.set_state("set_starswallet")
        return

    Userx.update(message.from_user.id, user_stars_wallet=username)
    await message.reply(i18n.get("successful_wallet"), reply_markup=back_menu(i18n))

@router.message(F.text, StateFilter("set_cardwallet"))
async def set_card_wallet(call: CallbackQuery, bot: Bot, state: FSM, i18n: I18nContext):
    message: str = "".join(ch for ch in call.text if ch.isdigit())
    await state.clear()

    if not validate_card(message):
        await call.reply(i18n.get("incorrect_card_wallet"))
        await state.set_state("set_cardwallet")
        return

    Userx.update(call.from_user.id, user_card_wallet=message)

    await call.reply(i18n.get("successful_wallet"), reply_markup=back_menu(i18n))



@router.callback_query(F.data == "yoomoney-wallet")
async def yoomoney_wallet_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()
    user = Userx.get(user_id=call.from_user.id)

    await call.message.edit_caption(
        caption=i18n.get(
            "add-wallet-yoomoney-exists",
            wallet=user.user_yoomoney_wallet
        ) if getattr(user, "user_yoomoney_wallet", None) is not None else i18n.get("add-wallet-yoomoney-not-exists"),
        reply_markup=back_menu(i18n)
    )
    await state.set_state("set_yoomoneywallet")


@router.message(F.text, StateFilter("set_yoomoneywallet"))
async def set_yoomoney_wallet(message: Message, bot: Bot, state: FSM, i18n: I18nContext):
    wallet = "".join(ch for ch in message.text if ch.isdigit())
    await state.clear()

    if not validate_yoomoney(wallet):
        await message.reply(i18n.get("incorrect_yoomoney_wallet"))
        await state.set_state("set_yoomoneywallet")
        return

    Userx.update(message.from_user.id, user_yoomoney_wallet=wallet)
    await message.reply(i18n.get("successful_wallet"), reply_markup=back_menu(i18n))

@router.callback_query(F.data.startswith("select_language:"))
async def change_language(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    locale = call.data.split(":")[1]
    await state.clear()

    try:
        await call.message.delete()
        await call.delete()
    except:
        ...

    await i18n.set_locale(locale)
    await show_home_menu(call.message, bot, state, i18n)


@router.callback_query(F.data == "generate_refferal")
async def generate_refferal(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    user = Userx.get(user_id=call.from_user.id)
    if user.user_ton_wallet is None:
        await call.answer(i18n.get("wallet_specified"), True)
        return

    await call.message.reply(
        i18n.get("referral-link-text",
                 bot_username=(await bot.get_me()).username,
                 user_wallet=user.user_ton_wallet,
                 referral_count=user.refferal_count,
                 referral_earnings=0.0)
    )


@router.message(F.text == "/support")
@router.callback_query(F.data == "support")
async def support_start(event: Union[Message, CallbackQuery], bot: Bot, state: FSM, i18n: I18nContext):
    """Команда /support или кнопка — приглашение написать в поддержку."""
    await state.clear()
    await state.set_state("support_message")

    text = i18n.get("support_prompt")
    markup = back_menu(i18n)

    if isinstance(event, CallbackQuery):
        await event.answer()
        await event.message.answer(text, reply_markup=markup)
    else:
        await event.answer(text, reply_markup=markup)


@router.message(F.text, StateFilter("support_message"))
async def support_receive(message: Message, bot: Bot, state: FSM, i18n: I18nContext):
    """Принимает сообщение пользователя и пересылает админам с кнопкой ответа."""
    await state.clear()

    user = message.from_user
    username = f"@{user.username}" if user.username else "без username"
    body = message.text or ""

    admin_text = ded(f"""
        📩 <b>Новое обращение в поддержку</b>

        👤 От: {username} (<code>{user.id}</code>)
        💬 Сообщение:
        {body}
    """)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from bot.utils.const_functions import ikb
    kb = InlineKeyboardBuilder()
    kb.row(ikb("✉️ Ответить", f"support_reply:{user.id}"))

    await send_admins(bot, admin_text, keyboard=kb.as_markup())

    await message.answer(i18n.get("support_sent"), reply_markup=back_menu(i18n))

