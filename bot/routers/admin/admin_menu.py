# - *- coding: utf- 8 - *-
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message, ReactionTypeEmoji
from aiogram_i18n import I18nContext
from pyexpat.errors import messages

from bot.database import Userx, Deals, Worker, Banx
from bot.keyboard.inline_admin import main_admin, admin_edits, admin_back, admin_markup_list, worker_edit, select_deals, \
    edit_deal, banlist_markup
from bot.keyboard.inline_user import select_wallet_method, back_menu, deal_markup, select_card_currency, deal_confirmed
from bot.utils.const_functions import generate_deal_id, is_float, ded, convert_date, convert_day, get_unix, \
    is_wallet_ton
from bot.data.config import get_admins
from bot.utils.misc.bot_models import FSM, ARS

router = Router(name=__name__)


@router.message(F.text == "/admin_panelb")
async def admin_panelb(message: Message, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    worker = Worker.get(worker_id=message.from_user.id)

    if worker is None:
        admin_menu = await message.answer(
            ded(f"""
                🎉 <b>Вы перешли в админ-панель!</b>
                
                💎 <b>Ваша роль:</b> <code>Владелец</code>

                🔧 Здесь вы можете управлять сделками и участниками.
                👑 Добро пожаловать в эксклюзивный доступ!
                    """),
            reply_markup=main_admin(True)
        )
        await bot.set_message_reaction(chat_id=admin_menu.chat.id, message_id=admin_menu.message_id,
                                       reaction=[{"type": "emoji", "emoji": "👨‍💻"}])
        return

    admin_menu = await message.answer(
        ded(f"""
                    🎉 <b>Вы перешли в админ-панель!</b>
                    
                    💎 <b>Ваша роль:</b> <code>Воркер</code>
                    📌 <b>Ваш префикс:</b> <code>{worker.worker_prefix}</code>

                    🔧 Здесь вы можете управлять сделками и участниками.
                    👑 Добро пожаловать в эксклюзивный доступ!
                """),
        reply_markup=main_admin()
    )

    await bot.set_message_reaction(chat_id=admin_menu.chat.id, message_id=admin_menu.message_id,
                                   reaction=[{"type": "emoji", "emoji": "👨‍💻"}])


@router.callback_query(F.data == "back_admin")
async def back_admin(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    worker = Worker.get(worker_id=call.from_user.id)

    if worker is None:
        admin_menu = await call.message.edit_text(
            ded(f"""
                🎉 <b>Вы перешли в админ-панель!</b>

                💎 <b>Ваша роль:</b> <code>Владелец</code>

                🔧 Здесь вы можете управлять сделками и участниками.
                👑 Добро пожаловать в эксклюзивный доступ!
                    """),
            reply_markup=main_admin(True)
        )
        await bot.set_message_reaction(chat_id=admin_menu.chat.id, message_id=admin_menu.message_id,
                                       reaction=[{"type": "emoji", "emoji": "👨‍💻"}])
        return

    admin_menu = await call.message.edit_text(
        ded(f"""
                    🎉 <b>Вы перешли в админ-панель!</b>

                    💎 <b>Ваша роль:</b> <code>Воркер</code>
                    📌 <b>Ваш префикс:</b> <code>{worker.worker_prefix}</code>

                    🔧 Здесь вы можете управлять сделками и участниками.
                    👑 Добро пожаловать в эксклюзивный доступ!
                """),
        reply_markup=main_admin()
    )

    await bot.set_message_reaction(chat_id=admin_menu.chat.id, message_id=admin_menu.message_id,
                                   reaction=[{"type": "emoji", "emoji": "👨‍💻"}])


@router.callback_query(F.data == "manage_admins")
async def manage_admins(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    worker = Worker.get(worker_id=call.from_user.id)

    if worker is not None:
        return

    await call.message.edit_text(ded("""
        👥 <b>Управление администраторами</b>
        Выберите действие из меню ниже.
    """),
                                 reply_markup=admin_edits())


@router.callback_query(F.data == "admin_add")
async def admin_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    worker = Worker.get(worker_id=call.from_user.id)

    if worker is not None:
        return

    await call.message.edit_text(ded("""
        ➕ <b>Добавление воркера.</b>
        
        Введите username пользователя для добавления в формате: <code>@example_username</code>
    """), reply_markup=admin_back())
    await state.set_state("admin_add_name")


@router.message(F.text, StateFilter("admin_add_name"))
async def admin_add_name(message: Message, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    username = message.text.replace("@", "")
    await state.clear()

    worker = Worker.get(worker_id=message.from_user.id)

    if worker is not None:
        return

    user = Userx.get(user_login=username.lower())

    if user is None:
        await message.answer(ded(f"""
            ❌ Пользователь `<code>@{username}</code>` не найден в боте. Попробуйте еще раз.
        """))
        await state.set_state("admin_add_name")
        return

    if user.user_id == message.from_user.id:
        await message.answer(ded(f"""
                ❌ Вы владелец и не можете добавить себя в воркеры. Попробуйте еще раз.
            """))
        await state.set_state("admin_add_name")
        return

    await message.answer(ded("""
            📌 Введите заметку для воркера: 
        """), reply_markup=admin_back())

    await state.update_data(username=username.lower())
    await state.set_state("admin_add_prefix")


@router.message(F.text, StateFilter("admin_add_prefix"))
async def admin_add_prefix(message: Message, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    username = (await state.get_data())['username']
    prefix = message.text
    await state.clear()

    worker = Worker.get(worker_id=message.from_user.id)

    if worker is not None:
        return

    user = Userx.get(user_login=username)

    Worker.add(
        worker_id=user.user_id,
        worker_prefix=prefix,
    )

    await message.answer(ded(f"""
                ✅ <b>Воркер успешно добавлен.</b>
                
                📌 Префикс: <code>{prefix}</code>
                👤 Пользователь: @{user.user_login} ({user.user_id})
            """), reply_markup=admin_back())

    await state.set_state("admin_add_prefix")


@router.callback_query(F.data == "admin_list")
async def admin_list(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    await call.message.edit_text(ded(f"""
            📋 Выберите воркера из списка ниже для редактирования.
            
            ⚠️ В этом списке не отображаются создатели бота. Измените их в конфиге бота
        """), reply_markup=admin_markup_list())


@router.callback_query(F.data == "add_stats")
async def add_stats(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    await call.message.edit_text(ded(f"""
            💬 <b>Введите количество успешных сделок которое будет отображаться у вас в профиле:</b> 
        """), reply_markup=admin_back())

    await state.set_state("get_add_stat_sdels")


@router.callback_query(F.data == "admin_deals")
async def add_stats(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    await state.clear()

    worker = Worker.get(worker_id=call.from_user.id)

    deals_count = 0

    for deal in Deals.get_all():
        if (worker is None and worker is None) or \
                (worker is not None and deal.deal_member == worker.worker_id):
            deals_count += 1
    await call.message.edit_text(ded(f"""
            📈 Выберите сделку ({deals_count})
            
            ⚠️ Показываются последние 30 сделок.
            ⚠️ Показываются только сделки где вы являетесь участником.
        """), reply_markup=select_deals(worker, worker is None))


@router.message(F.text, StateFilter("get_add_stat_sdels"))
async def get_add_stat_sdels(message: Message, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    sucessful_deals = message.text
    await state.clear()

    Userx.update(user_id=message.from_user.id, sucessful_deals=sucessful_deals)
    await message.answer(ded(f"""
            ✅ <b>Количество успешных сделок в профиле успешно изменено</b>
        """))

    await state.clear()


@router.callback_query(F.data.startswith("admin_workers_page"))
async def admin_workers_page(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    page = call.data.split(":")[1]
    await state.clear()

    await call.message.edit_text(ded(f"""
        📋 Выберите воркера из списка ниже для редактирования.
            
        ⚠️ В этом списке не отображаются создатели бота. Измените их в конфиге бота
    """), reply_markup=admin_markup_list(int(page)))




@router.callback_query(F.data.startswith("select_worker:"))
async def select_worker(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    worker_id = call.data.split(":")[1]
    await state.clear()

    worker = Worker.get(worker_id=worker_id)
    worker_user = Userx.get(user_id=worker_id)
    how_days = int(get_unix() - worker.worker_set_unix) // 60 // 60 // 24

    await call.message.edit_text(ded(f"""
                👤 <b>Воркер @{worker_user.user_login} <b>({worker.worker_id})</b> - №{worker.increment}</b>
                
                📌 <b>Префикс:</b> {worker.worker_prefix}.
                
                🕘 <b>Добавлен:</b> {convert_date(worker.worker_set_unix, True, False)}.
                
                ✅ <b>Успешных сделок:</b> {worker.worker_deals_sucessful}.
                
                ❌ <b>Отмененных сделок:</b> {worker.worker_deals_cancel}.
        """), reply_markup=worker_edit(worker_id))


@router.callback_query(F.data.startswith("worker_delete:"))
async def select_worker(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    worker_id = call.data.split(":")[1]
    await state.clear()

    worker = Worker.get(worker_id=call.from_user.id)

    if worker is not None:
        return

    Worker.delete(worker_id=worker_id)

    await call.answer("❌ Воркер удален")

    await back_admin(call, bot, state, arSession, i18n)


@router.callback_query(F.data.startswith("edit_deal:"))
async def edat_deal(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    deal_id = call.data.split(":")[1]
    await state.clear()

    deal = Deals.get(deal_id=deal_id)

    if deal is None:
        await call.answer("❌ Данная сделка уже удалена.", show_alert=True)
        return

    deal_owner = Userx.get(user_id=deal.deal_owner_id) if deal.deal_owner_id else None
    if deal_owner is None:
        # Совместимость со старыми сделками.
        if deal.deal_payment_method == "ton":
            deal_owner = Userx.get(user_ton_wallet=deal.deal_address)
        elif deal.deal_payment_method == "card":
            deal_owner = Userx.get(user_card_wallet=deal.deal_address)
        else:
            deal_owner = Userx.get(user_stars_wallet=deal.deal_address)
    deal_member = Userx.get(user_id=deal.deal_member)

    await call.message.edit_text(ded(f"""
            💼 Сделка #{deal.deal_id}
            
            📌 Продавец:
            👤 {deal_owner.user_name} (<code>{deal_owner.user_id}</code>)
            • Юзернейм: @{deal_owner.user_login}
            
            📌 <b>Покупатель:</b>
            {f'''
            👤 {deal_member.user_name} (<code>{deal_member.user_id}</code>)
            • Юзернейм: @{deal_member.user_login}
            ''' if deal_member is not None else 'Не установлен'}
            
            ✉️ <b>Описание сделки</b>: {deal.deal_description}
            
            💰 <b>Сумма</b>: {deal.deal_amount} {("Stars" if deal.deal_payment_method == "stars" or deal.deal_currency == "XTR" else deal.deal_currency.upper())}
        """), reply_markup=edit_deal(deal.deal_id))


@router.callback_query(F.data.startswith("cancel_deal:"))
async def cancel_deal(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    deal_id = call.data.split(":")[1]
    await state.clear()

    deal = Deals.get(deal_id=deal_id)

    if deal is None:
        await call.answer("❌ Данная сделка уже удалена", True)
        return

    Deals.update(deal_id=deal_id, deal_status="pending delete")
    Deals.delete(deal_id=deal_id)

    await call.message.edit_text(
        "✅ Сделка успешно удалена",
        reply_markup=admin_back()
    )


@router.callback_query(F.data.startswith("confirm_deal:"))
async def confirm_deal(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    deal_id = call.data.split(":")[1]
    await state.clear()

    deal = Deals.get(deal_id=deal_id)

    if deal is None:
        await call.answer("❌ Данная сделка уже удалена", True)
        return

    deal_owner = Userx.get(user_id=deal.deal_owner_id) if deal.deal_owner_id else None
    if deal_owner is None:
        # Совместимость со старыми сделками.
        if deal.deal_payment_method == "ton":
            deal_owner = Userx.get(user_ton_wallet=deal.deal_address)
        elif deal.deal_payment_method == "card":
            deal_owner = Userx.get(user_card_wallet=deal.deal_address)
        else:
            deal_owner = Userx.get(user_stars_wallet=deal.deal_address)

    deal_member = Userx.get(user_id=deal.deal_member)

    if deal is None:
        await call.answer("❌ Данная сделка уже удалена", True)
        return

    if deal_member is None:
        await call.answer("❌ Для подтверждения сделки нужно чтобы в ней был покупатель.", True)
        return

    if deal.deal_status == "paided":
        await call.answer("❌ Данная сделка уже оплачена.", True)
        return

    Deals.update(deal_id=deal_id, deal_status="paided")

    try:
        await call.answer("✅ Оплата для сделки успешно подтверждена.")
        await call.message.edit_text(ded(f"""
            ✅ Оплата для сделки успешно подтверждена.
        """), reply_markup=admin_back())

        await bot.send_message(
            chat_id=deal_owner.user_id,
            text=i18n.get("deal_paid", deal_id=deal.deal_id, deal_description=deal.deal_description,
                          deal_member_username=deal_member.user_login),
            reply_markup=deal_confirmed(i18n, f"https://t.me/{deal_member.user_login}", deal.deal_id)
        )

        await bot.send_message(
            chat_id=deal_member.user_id,
            text=i18n.get("deal_paid_member", deal_id=deal.deal_id),
            reply_markup=back_menu(i18n)
        )
    except:
        Deals.delete(deal_id=deal_id)
        await call.message.answer(" К сожалению не удалось подтвердить оплату для сделки.", reply_markup=admin_back())
        await call.message.delete()



@router.callback_query(F.data == "admin_ban")
async def admin_ban_start(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    if call.from_user.id not in get_admins():
        await call.answer("Только для администраторов.", show_alert=True)
        return
    await state.clear()
    await call.message.edit_text(
        ded("""
            🚫 <b>Бан пользователя</b>

            Отправьте <b>username</b> пользователя (с @ или без).
            Пример: <code>@username</code> или <code>username</code>
        """),
        reply_markup=admin_back()
    )
    await state.set_state("admin_ban_username")


@router.message(F.text, StateFilter("admin_ban_username"))
async def admin_ban_username(message: Message, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    if message.from_user.id not in get_admins():
        await state.clear()
        return

    username = message.text.strip().lstrip("@").lower()
    if not username or " " in username:
        await message.answer("Укажите корректный username одним словом.")
        return

    user = Userx.get(user_login=username)
    if user is None:
        await message.answer(
            "Пользователь с таким username не найден в боте. Он должен хотя бы раз написать боту (/start)."
        )
        return

    if user.user_id in get_admins():
        await message.answer("Нельзя забанить администратора.")
        await state.clear()
        return

    await state.update_data(ban_user_id=user.user_id, ban_user_login=user.user_login)
    await message.answer(
        ded(f"""
            👤 Пользователь: @{user.user_login} (<code>{user.user_id}</code>)

            Отправьте <b>причину бана</b> одним сообщением.
        """),
        reply_markup=admin_back()
    )
    await state.set_state("admin_ban_reason")


@router.message(F.text, StateFilter("admin_ban_reason"))
async def admin_ban_reason(message: Message, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    if message.from_user.id not in get_admins():
        await state.clear()
        return

    data = await state.get_data()
    user_id = data.get("ban_user_id")
    user_login = data.get("ban_user_login") or ""
    reason = message.text.strip()
    await state.clear()

    if not user_id or not reason:
        await message.answer("Данные бана утеряны. Начните заново.")
        return

    Banx.add(
        user_id=user_id,
        user_login=user_login,
        reason=reason,
        banned_by=message.from_user.id,
    )

    await message.answer(
        ded(f"""
            ✅ Пользователь @{user_login} (<code>{user_id}</code>) забанен.

            📌 Причина: {reason}
        """),
        reply_markup=admin_back()
    )

    try:
        await bot.send_message(
            user_id,
            ded(f"""
                🚫 <b>Вы заблокированы в этом боте.</b>

                📌 <b>Причина:</b> {reason}
            """)
        )
    except Exception:
        await message.answer("Не удалось отправить уведомление пользователю (он мог заблокировать бота).")


@router.callback_query(F.data == "admin_banlist")
async def admin_banlist(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    if call.from_user.id not in get_admins():
        await call.answer("Только для администраторов.", show_alert=True)
        return
    await state.clear()
    bans = Banx.get_all()
    if not bans:
        await call.message.edit_text(
            "📋 <b>Банлист пуст.</b>\nЗабаненных пользователей нет.",
            reply_markup=admin_back()
        )
        return
    await call.message.edit_text(
        ded(f"""
            📋 <b>Банлист</b> ({len(bans)})

            Нажмите на пользователя, чтобы разбанить.
        """),
        reply_markup=banlist_markup(bans, page=0)
    )


@router.callback_query(F.data.startswith("admin_banlist_page:"))
async def admin_banlist_page(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    if call.from_user.id not in get_admins():
        await call.answer("Только для администраторов.", show_alert=True)
        return
    page = int(call.data.split(":")[1])
    bans = Banx.get_all()
    await call.message.edit_text(
        ded(f"""
            📋 <b>Банлист</b> ({len(bans)})

            Нажмите на пользователя, чтобы разбанить.
        """),
        reply_markup=banlist_markup(bans, page=page)
    )


@router.callback_query(F.data.startswith("admin_unban:"))
async def admin_unban(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    if call.from_user.id not in get_admins():
        await call.answer("Только для администраторов.", show_alert=True)
        return
    user_id = int(call.data.split(":")[1])
    ban = Banx.get(user_id=user_id)
    if ban is None:
        await call.answer("Пользователь уже не в бане.", show_alert=True)
        bans = Banx.get_all()
        if not bans:
            await call.message.edit_text(
                "📋 <b>Банлист пуст.</b>",
                reply_markup=admin_back()
            )
            return
        await call.message.edit_reply_markup(reply_markup=banlist_markup(bans, page=0))
        return

    Banx.delete(user_id=user_id)
    login = ban.user_login or str(user_id)
    await call.answer(f"@{login} разбанен", show_alert=True)

    try:
        await bot.send_message(
            user_id,
            "✅ <b>Вы были разблокированы</b> в этом боте. Можете снова пользоваться сервисом."
        )
    except Exception:
        pass

    bans = Banx.get_all()
    if not bans:
        await call.message.edit_text(
            "📋 <b>Банлист пуст.</b>\nЗабаненных пользователей нет.",
            reply_markup=admin_back()
        )
        return
    await call.message.edit_text(
        ded(f"""
            📋 <b>Банлист</b> ({len(bans)})

            Нажмите на пользователя, чтобы разбанить.
        """),
        reply_markup=banlist_markup(bans, page=0)
    )


@router.callback_query(F.data.startswith("support_reply:"))
async def support_reply_start(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    if call.from_user.id not in get_admins():
        await call.answer("Только для администраторов.", show_alert=True)
        return

    user_id = int(call.data.split(":")[1])
    await state.clear()
    await state.update_data(support_reply_to=user_id)
    await state.set_state("admin_support_reply")

    await call.answer()
    await call.message.answer(
        ded(f"""
            ✉️ <b>Ответ пользователю</b> <code>{user_id}</code>

            Напишите текст ответа одним сообщением.
            Для отмены нажмите /cancel или «Вернуться в меню».
        """),
        reply_markup=admin_back()
    )


@router.message(F.text == "/cancel", StateFilter("admin_support_reply"))
async def support_reply_cancel(message: Message, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    if message.from_user.id not in get_admins():
        return
    await state.clear()
    await message.answer("❌ Ответ отменён.", reply_markup=admin_back())


@router.message(F.text, StateFilter("admin_support_reply"))
async def support_reply_send(message: Message, bot: Bot, state: FSM, arSession: ARS, i18n: I18nContext):
    if message.from_user.id not in get_admins():
        await state.clear()
        return

    data = await state.get_data()
    user_id = data.get("support_reply_to")
    await state.clear()

    if not user_id:
        await message.answer("❌ Не удалось определить получателя. Начните заново.")
        return

    reply_body = message.text.strip()
    try:
        await bot.send_message(
            user_id,
            ded(f"""
                💬 <b>Ответ поддержки</b>

                {reply_body}
            """)
        )
        await message.answer(
            ded(f"""
                ✅ Ответ отправлен пользователю <code>{user_id}</code>.
            """),
            reply_markup=admin_back()
        )
    except Exception as e:
        await message.answer(
            ded(f"""
                ⚠️ Не удалось отправить сообщение пользователю <code>{user_id}</code>.
                Возможно, он заблокировал бота.
            """),
            reply_markup=admin_back()
        )

