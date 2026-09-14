# - *- coding: utf- 8 - *-
import re

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram_i18n import I18nContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.data.config import get_admins
from bot.database import Userx, Deals, Worker
from bot.keyboard.inline_user import (
    select_wallet_method, back_menu, deal_markup, select_card_currency,
    selectable_keyboard, deal_gift_sended_member
)
from bot.utils.const_functions import (
    generate_deal_id, is_float, send_admins, ded, get_date, send_owners,
    send_group, ikb
)
from bot.utils.misc.bot_models import FSM, ARS

router = Router(name=__name__)


def admin_confirmation_keyboard(i18n: I18nContext, deal_id: str, role: str) -> InlineKeyboardMarkup:
    """Кнопки подтверждения для админов-участников сделки.
    Подтверждение передачи товара — только у покупателя (confirm_goods).
    Продавец передаёт товар и при необходимости присылает скриншот.
    """
    keyboard = InlineKeyboardBuilder()
    if role == "buyer":
        keyboard.row(ikb("💰 Подтвердить передачу денег", f"test_confirm:buyer:{deal_id}"))
    # role == "seller": без кнопки «Подтвердить передачу товара»
    return keyboard.as_markup()


def get_deal_owner(deal):
    """Главное правило: владелец сделки хранится в deal_owner_id."""
    if deal.deal_owner_id:
        return Userx.get(user_id=deal.deal_owner_id)

    # Совместимость со старыми сделками, созданными до rework.
    # После миграции новые сделки никогда не определяют владельца по кошельку.
    if deal.deal_payment_method == "ton":
        return Userx.get(user_ton_wallet=deal.deal_address)
    if deal.deal_payment_method == "card":
        return Userx.get(user_card_wallet=deal.deal_address)
    if deal.deal_payment_method == "stars":
        return Userx.get(user_stars_wallet=deal.deal_address)
    if deal.deal_payment_method == "yoomoney":
        return Userx.get(user_yoomoney_wallet=deal.deal_address)
    return None


async def send_test_admin_notifications(bot: Bot, text: str, deal_id: str, owner_id: int, member_id: int = 0):
    """Уведомления тестерам. Кнопка появляется только у админа, являющегося участником сделки."""
    for admin_id in get_admins():
        keyboard = None
        if member_id and admin_id == member_id:
            keyboard = admin_confirmation_keyboard(None, deal_id, "buyer")
        # продавцу-админу кнопка подтверждения передачи товара не выдаётся

        try:
            await bot.send_message(
                admin_id,
                text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        except Exception:
            pass


@router.callback_query(F.data == "create_deal")
async def create_deal(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()
    user = Userx.get(user_id=call.from_user.id)

    if (
        user.user_ton_wallet is None
        and user.user_card_wallet is None
        and user.user_stars_wallet is None
        and getattr(user, "user_yoomoney_wallet", None) is None
    ):
        await call.answer(i18n.get("wallet_specified"), True)
        return

    await call.message.edit_caption(
        caption=i18n.get("select_payment_method"),
        reply_markup=select_wallet_method(
            i18n, True, user,
            "select_payment_method:ton",
            "select_payment_method:card"
        )
    )
    await state.set_state("select_payment")


@router.callback_query(F.data.startswith("select_payment_method:"), StateFilter("select_payment"))
async def select_payment_method(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    payment_method = call.data.split(":")[1]
    user = Userx.get(user_id=call.from_user.id)
    await state.clear()

    if payment_method == "card":
        await call.message.edit_caption(
            caption=i18n.get("select_payment_country"),
            reply_markup=select_card_currency(i18n)
        )
        await state.update_data(payment_method="card")
        await state.set_state("select_payment_country")
        return

    if payment_method == "stars":
        if user.user_stars_wallet is None:
            await call.answer(i18n.get("wallet_specified"), True)
            return

        await call.message.edit_caption(
            caption=i18n.get("deals_create", format="Telegram Stars"),
            reply_markup=back_menu(i18n)
        )
        await state.update_data(payment_method="stars", currency="Stars")
        await state.set_state("deal_amount")
        return
    if payment_method == "yoomoney":
        if getattr(user, "user_yoomoney_wallet", None) is None:
            await call.answer(i18n.get("wallet_specified"), True)
            return

        await call.message.edit_caption(
            caption=i18n.get("deals_create", format="RUB (ЮMoney)"),
            reply_markup=back_menu(i18n)
        )
        await state.update_data(payment_method="yoomoney", currency="RUB")
        await state.set_state("deal_amount")
        return


    await call.message.edit_caption(
        caption=i18n.get("deals_create", format="TON"),
        reply_markup=back_menu(i18n)
    )
    await state.update_data(payment_method="ton", currency="TON")
    await state.set_state("deal_amount")


@router.callback_query(F.data.startswith("select_currency:"), StateFilter("select_payment_country"))
async def select_payment_country(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    data = await state.get_data()
    currency = call.data.split(":")[1]
    await state.clear()

    await call.message.edit_caption(
        caption=i18n.get("deals_create", format=currency.upper()),
        reply_markup=back_menu(i18n)
    )
    await state.update_data(
        payment_method=data["payment_method"],
        currency=currency.upper()
    )
    await state.set_state("deal_amount")


@router.message(F.text, StateFilter("deal_amount"))
async def deal_amount(message: Message, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    data = await state.get_data()
    payment_method = data["payment_method"]
    currency = data["currency"]
    raw_amount = message.text.strip()

    if payment_method == "stars":
        if not raw_amount.isdigit() or int(raw_amount) <= 0:
            await message.reply(i18n.get("invalid_stars_amount"))
            return
        deal_amount = int(raw_amount)
    else:
        if not is_float(raw_amount) or float(raw_amount) <= 0:
            await message.reply(i18n.get("invalid_amount_format"))
            return
        deal_amount = raw_amount

    await state.clear()
    await message.reply(i18n.get("deal_description"), reply_markup=back_menu(i18n))
    await state.update_data(
        payment_method=payment_method,
        deal_amount=deal_amount,
        currency=currency
    )
    await state.set_state("deal_description")


@router.message(F.text, StateFilter("deal_description"))
async def deal_description(message: Message, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    data = await state.get_data()
    payment_method = data["payment_method"]
    deal_amount = data["deal_amount"]
    deal_currency = data["currency"]
    deal_description = message.text.strip()

    await state.clear()

    user = Userx.get(user_id=message.from_user.id)
    deal_id = generate_deal_id()

    if payment_method == "ton":
        address = user.user_ton_wallet
    elif payment_method == "card":
        address = user.user_card_wallet
    elif payment_method == "stars":
        address = user.user_stars_wallet
    elif payment_method == "yoomoney":
        address = getattr(user, "user_yoomoney_wallet", None)
    else:
        await message.reply("❌ Неизвестный способ оплаты.")
        return

    if address is None:
        await message.reply(i18n.get("wallet_specified"))
        return

    numeric_amount = float(deal_amount) if payment_method != "stars" else int(deal_amount)

    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: владелец = тот, кто нажал "Создать сделку".
    # Кошелек используется только как реквизит для оплаты.
    Deals.add(
        deal_id=deal_id,
        deal_amount=numeric_amount,
        deal_currency=deal_currency,
        deal_description=deal_description,
        deal_address=address,
        deal_owner_id=user.user_id,
        deal_payment_method=payment_method
    )

    user_status = "пользователь"
    if Worker.get(worker_id=user.user_id):
        user_status = "воркер"
    if user.user_id in get_admins():
        user_status = "владелец"

    admin_text = ded(f"""
        ✅ Новая сделка: {user_status} @{user.user_login} создал сделку #{deal_id}!

        💰 Сумма: <code>{numeric_amount} {deal_currency}</code>
        📄 Описание: {deal_description}
        📅 Дата создания: {get_date(True)}

        👤 Создатель/продавец: @{user.user_login} (<b>{user.user_id}</b>)

        ⚠️ Это сообщение отправляется тестерам/создателям бота.
    """)

    await send_test_admin_notifications(
        bot, admin_text, deal_id, user.user_id, 0
    )

    amount_format = "Stars" if payment_method == "stars" else deal_currency

    if payment_method == "stars":
        payment_details = f"⭐ Получатель Stars: @{address}"
    elif payment_method == "ton":
        payment_details = f"💎 TON-кошелек для оплаты: <code>{address}</code>"
    elif payment_method == "yoomoney":
        payment_details = f"💜 ЮMoney для оплаты: <code>{address}</code>"
    else:
        payment_details = f"💳 Карта для оплаты: <code>{address}</code>"

    own_keyboard = deal_markup(
        i18n, False, deal_id,
        payment_method=payment_method
    )
    # Продавцу не выдаём кнопку «Подтвердить передачу товара» (в т.ч. админам)

    await message.reply(
        i18n.get(
            "sucessful_create_deal",
            deal_amount=str(numeric_amount),
            deal_amount_format=amount_format,
            deal_description=deal_description,
            bot_username=(await bot.get_me()).username,
            deal_id=deal_id,
            payment_details=payment_details
        ),
        reply_markup=own_keyboard
    )


@router.callback_query(F.data.startswith("test_confirm:"))
async def test_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    _, role, deal_id = call.data.split(":", 2)

    if call.from_user.id not in get_admins():
        await call.answer("❌ Эта кнопка доступна только тестерам.", show_alert=True)
        return

    deal = Deals.get(deal_id=deal_id)
    if deal is None:
        await call.answer("❌ Сделка уже удалена.", show_alert=True)
        return

    owner = get_deal_owner(deal)
    member = Userx.get(user_id=deal.deal_member) if deal.deal_member else None

    if owner is None or member is None:
        await call.answer("❌ В сделке пока нет обоих участников.", show_alert=True)
        return

    if role == "seller":
        if call.from_user.id != owner.user_id:
            await call.answer("❌ Вы не продавец этой сделки.", show_alert=True)
            return
        if deal.seller_confirmed:
            await call.answer("ℹ️ Передача товара уже подтверждена.", show_alert=True)
            return

        Deals.update(deal_id, seller_confirmed=1)
        await call.answer("✅ Передача товара подтверждена.")
        try:
            await call.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

        await bot.send_message(
            member.user_id,
            i18n.get(
                "test_seller_confirmed",
                deal_id=deal_id,
                seller_username=owner.user_login,
                payment_details=(
                    f"⭐ Получатель Stars: @{deal.deal_address}"
                    if deal.deal_payment_method == "stars"
                    else (
                        f"💎 TON-кошелек для оплаты: <code>{deal.deal_address}</code>"
                        if deal.deal_payment_method == "ton"
                        else f"💳 Карта для оплаты: <code>{deal.deal_address}</code>"
                    )
                )
            ),
            reply_markup=back_menu(i18n)
        )
        return

    if role == "buyer":
        if call.from_user.id != member.user_id:
            await call.answer("❌ Вы не покупатель этой сделки.", show_alert=True)
            return
        if deal.buyer_confirmed:
            await call.answer("ℹ️ Передача денег уже подтверждена.", show_alert=True)
            return

        Deals.update(deal_id, buyer_confirmed=1, deal_status="transfer_goods")
        await call.answer("✅ Передача денег подтверждена.")
        try:
            await call.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

        # Для продавца: средства подтверждены поддержкой, нужно передать товар.
        await bot.send_message(
            owner.user_id,
            i18n.get("test_buyer_confirmed", deal_id=deal_id, buyer_username=member.user_login),
            reply_markup=back_menu(i18n)
        )

        # Покупатель: ожидает товар + кнопка подтверждения передачи
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from bot.utils.const_functions import ikb
        kb = InlineKeyboardBuilder()
        kb.row(ikb(i18n.get("confirm_goods_received"), f"confirm_goods:{deal_id}"))
        await bot.send_message(
            member.user_id,
            i18n.get("test_buyer_confirmed_member", deal_id=deal_id),
            reply_markup=kb.as_markup()
        )


@router.callback_query(F.data.startswith("deal_select:"))
async def deal_select(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    deal_id = call.data.split(":")[1]
    deal_status = call.data.split(":")[2]
    await state.clear()

    deal = Deals.get(deal_id=deal_id)
    if deal is None:
        return

    if deal_status == "yes":
        Deals.delete(deal_id=deal_id)
        await call.message.delete()
        await call.answer(i18n.get("deal_deleted"), True)
        await call.message.answer(i18n.get("deal_deleted"))
        await send_owners(bot, ded(f"""
            📄 <b>Информация о сделке #{deal_id}</b>
            Сделка была удалена.
            ⚠️ Это сообщение отправляется только создателям бота.
        """))
    else:
        await call.message.delete()
        await call.answer(i18n.get("deal_cancel_delete"), False)


@router.callback_query(F.data.startswith("exit_deal:"))
async def exit_deal(call: CallbackQuery, bot: Bot, state: FSM, i18n: I18nContext):
    deal_id = call.data.split(":")[1]
    await state.clear()
    await call.message.reply(
        i18n.get("exit_deal_text", deal_id=deal_id),
        reply_markup=selectable_keyboard(
            i18n.get("exit_yes"), f"deal_select_exit:{deal_id}:yes",
            i18n.get("exit_no"), f"deal_select_exit:{deal_id}:no"
        )
    )


@router.callback_query(F.data.startswith("deal_select_exit:"))
async def deal_select_exit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    deal_id = call.data.split(":")[1]
    exit_status = call.data.split(":")[2]
    await state.clear()

    deal = Deals.get(deal_id=deal_id)
    if deal is None:
        return

    owner = get_deal_owner(deal)
    member = Userx.get(user_id=deal.deal_member) if deal.deal_member else None

    if exit_status == "yes":
        Deals.update(deal_id=deal_id, deal_member=0, seller_confirmed=0, buyer_confirmed=0)
        await call.answer(i18n.get("deal_exited"), True)
        await call.message.answer(i18n.get("deal_exited"))

        if owner:
            await bot.send_message(
                owner.user_id,
                i18n.get(
                    "exited_deal",
                    exit_username=call.from_user.username or "unknown",
                    exit_id=str(call.from_user.id),
                    deal_id=deal_id
                )
            )

        if owner and member:
            await send_owners(bot, ded(f"""
                📄 <b>Информация о сделке #{deal.deal_id}</b>
                Пользователь @{call.from_user.username} ({call.from_user.id}) вышел из сделки.

                💰 <b>Сумма:</b> <code>{deal.deal_amount} {deal.deal_currency}</code>
                📄 <b>Описание:</b> {deal.deal_description}

                👤 <b>Создатель:</b> @{owner.user_login} ({owner.user_id})
                👤 <b>Участник:</b> @{member.user_login} ({member.user_id})
            """))
    else:
        await call.message.delete()
        await call.answer(i18n.get("deal_cancel_delete"), False)


@router.callback_query(F.data.startswith("delete_deal:"))
async def delete_deal(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    deal_id = call.data.split(":")[1]
    await state.clear()

    if Deals.get(deal_id=deal_id) is None:
        await call.message.delete()
        return

    await call.message.reply(
        i18n.get("cancel_deal_text", deal_id=deal_id),
        reply_markup=selectable_keyboard(
            i18n.get("cancel_yes"), f"deal_select:{deal_id}:yes",
            i18n.get("cancel_no"), f"deal_select:{deal_id}:no"
        )
    )


@router.callback_query(F.data.startswith("deal_gift_sended:"))
async def deal_gift_sended(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    deal_id = call.data.split(":")[1]
    await state.clear()
    deal = Deals.get(deal_id=deal_id)

    if deal is None or not deal.deal_member:
        try:
            await call.message.delete()
        except Exception:
            pass
        return

    owner = get_deal_owner(deal)
    member = Userx.get(user_id=deal.deal_member)
    if owner is None or member is None:
        return

    await call.message.delete()
    Deals.update(deal_id, seller_confirmed=1)

    await bot.send_message(owner.user_id, i18n.get("deal_gift_sended"))
    await bot.send_message(
        member.user_id,
        i18n.get("deal_gift_sended_member", deal_owner_username=owner.user_login),
        reply_markup=deal_gift_sended_member(i18n, deal_id)
    )


@router.callback_query(F.data.startswith("gift_earned:"))
async def gift_earned(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    deal_id = call.data.split(":")[1]
    await state.clear()
    deal = Deals.get(deal_id=deal_id)

    if deal is None or not deal.deal_member:
        try:
            await call.message.delete()
        except Exception:
            pass
        return

    owner = get_deal_owner(deal)
    member = Userx.get(user_id=deal.deal_member)
    if owner is None or member is None:
        return

    await call.message.delete()
    Deals.update(deal_id, deal_status="ended", buyer_confirmed=1)

    await bot.send_message(owner.user_id, i18n.get("deal_member_da"))
    await bot.send_message(owner.user_id, i18n.get("deal_ended_owner", deal_id=deal_id))
    await bot.send_message(member.user_id, i18n.get("deal_ended", deal_id=deal_id))

    await send_owners(bot, ded(f"""
        📄 <b>Информация о сделке #{deal.deal_id}</b>
        Сделка #{deal.deal_id} была завершена.

        💰 <b>Сумма:</b> <code>{deal.deal_amount} {deal.deal_currency}</code>
        📄 <b>Описание:</b> {deal.deal_description}

        👤 <b>Создатель:</b> @{owner.user_login} ({owner.user_id})
        👤 <b>Участник:</b> @{member.user_login} ({member.user_id})
    """))

    await send_group(bot, ded(f"""
        📄 <b>Сделка #{deal.deal_id} была завершена.</b>
        💰 <b>Сумма:</b> <code>{deal.deal_amount} {deal.deal_currency}</code>
        ℹ️ <b>Описание:</b> {deal.deal_description}
        👤 <b>Создатель/продавец:</b> @{owner.user_login} ({owner.user_id})
        👤 <b>Покупатель:</b> @{member.user_login} ({member.user_id})
    """))

    # Deals.delete(deal_id=deal_id)  # храним сделки


@router.callback_query(F.data.startswith("confirm_goods:"))
async def confirm_goods_received(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    """Покупатель подтверждает получение товара после оплаты."""
    deal_id = call.data.split(":", 1)[1]
    await state.clear()
    deal = Deals.get(deal_id=deal_id)

    if deal is None or not deal.deal_member:
        try:
            await call.message.delete()
        except Exception:
            pass
        return

    if call.from_user.id != deal.deal_member:
        await call.answer("❌ Только покупатель может подтвердить получение.", show_alert=True)
        return

    if deal.deal_status == "ended":
        await call.answer("ℹ️ Сделка уже завершена.", show_alert=True)
        return

    owner = get_deal_owner(deal)
    member = Userx.get(user_id=deal.deal_member)
    if owner is None or member is None:
        return

    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    Deals.update(deal_id, deal_status="ended", seller_confirmed=1, buyer_confirmed=1)

    await bot.send_message(owner.user_id, i18n.get("deal_member_da"))
    await bot.send_message(owner.user_id, i18n.get("deal_ended_owner", deal_id=deal_id))
    await bot.send_message(member.user_id, i18n.get("deal_ended", deal_id=deal_id))

    await send_owners(bot, ded(f"""
        📄 <b>Информация о сделке #{deal.deal_id}</b>
        Сделка #{deal.deal_id} была завершена (покупатель подтвердил получение товара).

        💰 <b>Сумма:</b> <code>{deal.deal_amount} {deal.deal_currency}</code>
        📄 <b>Описание:</b> {deal.deal_description}

        👤 <b>Создатель:</b> @{owner.user_login} ({owner.user_id})
        👤 <b>Участник:</b> @{member.user_login} ({member.user_id})
    """))

    await send_group(bot, ded(f"""
        📄 <b>Сделка #{deal.deal_id} была завершена.</b>
        💰 <b>Сумма:</b> <code>{deal.deal_amount} {deal.deal_currency}</code>
        ℹ️ <b>Описание:</b> {deal.deal_description}
        👤 <b>Создатель/продавец:</b> @{owner.user_login} ({owner.user_id})
        👤 <b>Покупатель:</b> @{member.user_login} ({member.user_id})
    """))

    # Сделки хранятся: помечаем ended, не удаляем
    # Deals.delete(deal_id=deal_id)  # отключено — храним историю


@router.message(F.photo)
async def seller_screenshot_handler(message: Message, bot: Bot, state: FSM, i18n: I18nContext):
    """Если продавец в периоде передачи товара присылает скриншот — благодарим."""
    user_id = message.from_user.id
    # Ищем сделки где пользователь продавец и статус transfer_goods
    deals = Deals.gets(deal_owner_id=user_id)
    active = [d for d in deals if d.deal_status == "transfer_goods" and d.buyer_confirmed]
    if not active:
        # также старые сделки без owner_id
        all_deals = Deals.get_all()
        for d in all_deals:
            if d.deal_status != "transfer_goods" or not d.buyer_confirmed:
                continue
            owner = get_deal_owner(d)
            if owner and owner.user_id == user_id:
                active.append(d)
    if not active:
        return  # не реагируем на чужие фото

    await message.reply(i18n.get("screenshot_received"))


@router.message(F.text == "/deals")
async def my_deals_cmd(message: Message, bot: Bot, state: FSM, i18n: I18nContext):
    """Список сделок пользователя (создатель или участник)."""
    await state.clear()
    user_id = message.from_user.id
    owned = Deals.gets(deal_owner_id=user_id)
    membered = [d for d in Deals.get_all() if d.deal_member == user_id]
    # убрать дубли
    seen = set()
    deals = []
    for d in owned + membered:
        if d.deal_id in seen:
            continue
        if d.deal_status == "ended":
            continue
        seen.add(d.deal_id)
        deals.append(d)

    if not deals:
        await message.answer(i18n.get("no_deals"), reply_markup=back_menu(i18n))
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from bot.utils.const_functions import ikb
    kb = InlineKeyboardBuilder()
    for d in deals:
        is_owner = (d.deal_owner_id == user_id) or (
            get_deal_owner(d) and get_deal_owner(d).user_id == user_id
        )
        status = d.deal_status or "waiting"
        label = (
            i18n.get("deal_item_owner", deal_id=d.deal_id, amount=str(d.deal_amount), currency=d.deal_currency, status=status)
            if is_owner else
            i18n.get("deal_item_member", deal_id=d.deal_id, amount=str(d.deal_amount), currency=d.deal_currency, status=status)
        )
        kb.row(ikb(label[:60], f"mydeal:{d.deal_id}"))
    kb.row(ikb(i18n.get("back"), "back"))
    await message.answer(i18n.get("my_deals_title"), reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("mydeal:"))
async def mydeal_manage(call: CallbackQuery, bot: Bot, state: FSM, i18n: I18nContext):
    deal_id = call.data.split(":", 1)[1]
    deal = Deals.get(deal_id=deal_id)
    if deal is None:
        await call.answer(i18n.get("invalid_deal_id"), True)
        return

    user_id = call.from_user.id
    owner = get_deal_owner(deal)
    is_owner = owner and owner.user_id == user_id
    is_member = deal.deal_member == user_id

    if not is_owner and not is_member:
        await call.answer("❌ Это не ваша сделка.", show_alert=True)
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from bot.utils.const_functions import ikb
    kb = InlineKeyboardBuilder()
    kb.row(ikb(i18n.get("continue_deal"), f"continue_deal:{deal_id}"))
    if is_owner:
        kb.row(ikb(i18n.get("delete_deal_btn"), f"delete_deal:{deal_id}"))
    if is_member:
        kb.row(ikb(i18n.get("leave_deal_btn"), f"exit_deal:{deal_id}"))
    kb.row(ikb(i18n.get("back"), "back"))

    role = "Продавец" if is_owner else "Покупатель"
    text = ded(f"""
        📄 <b>Сделка #{deal.deal_id}</b>
        👤 Роль: {role}
        💰 Сумма: <code>{deal.deal_amount} {deal.deal_currency}</code>
        📜 Описание: {deal.deal_description}
        📌 Статус: <code>{deal.deal_status}</code>
        📞 Поддержка: /support
    """)
    await call.message.edit_text(text, reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("continue_deal:"))
async def continue_deal(call: CallbackQuery, bot: Bot, state: FSM, i18n: I18nContext):
    """Продолжить сделку: показать актуальный статус и кнопки."""
    deal_id = call.data.split(":", 1)[1]
    deal = Deals.get(deal_id=deal_id)
    if deal is None:
        await call.answer(i18n.get("invalid_deal_id"), True)
        return

    user_id = call.from_user.id
    owner = get_deal_owner(deal)
    is_owner = owner and owner.user_id == user_id
    is_member = deal.deal_member == user_id

    if deal.deal_status == "transfer_goods" and is_member:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from bot.utils.const_functions import ikb
        kb = InlineKeyboardBuilder()
        kb.row(ikb(i18n.get("confirm_goods_received"), f"confirm_goods:{deal_id}"))
        await call.message.edit_text(
            i18n.get("deal_transfer_waiting_buyer", deal_id=deal_id),
            reply_markup=kb.as_markup()
        )
        return

    if deal.deal_status == "transfer_goods" and is_owner:
        await call.message.edit_text(
            i18n.get("deal_transfer_waiting_seller", deal_id=deal_id),
            reply_markup=back_menu(i18n)
        )
        return

    # По умолчанию — info
    if is_member and owner:
        paid_text = (
            f"⭐ Получатель Stars: @{deal.deal_address}"
            if deal.deal_payment_method == "stars"
            else (
                f"💎 TON: <code>{deal.deal_address}</code>"
                if deal.deal_payment_method == "ton"
                else f"💳 Карта: <code>{deal.deal_address}</code>"
            )
        )
        await call.message.edit_text(
            i18n.get(
                "deal_info",
                deal_id=deal.deal_id,
                username=owner.user_login,
                user_id=str(owner.user_id),
                deals_count=owner.sucessful_deals,
                deal_description=deal.deal_description,
                deal_address=deal.deal_address,
                paid_text=paid_text,
                deal_amount=deal.deal_amount,
                currency=("Stars" if deal.deal_payment_method == "stars" else deal.deal_currency),
                payment_details=paid_text
            ),
            reply_markup=deal_markup(
                i18n, True, deal.deal_id,
                deal.deal_address,
                deal.deal_payment_method == "ton",
                deal.deal_amount,
                deal.deal_payment_method
            )
        )
        return

    await call.message.edit_text(
        ded(f"""
            📄 <b>Сделка #{deal.deal_id}</b>
            💰 {deal.deal_amount} {deal.deal_currency}
            📜 {deal.deal_description}
            📌 Статус: {deal.deal_status}
        """),
        reply_markup=back_menu(i18n)
    )
