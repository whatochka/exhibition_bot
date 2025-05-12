from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from app.models import subzone
from app.models.item import Item
from app.models.subzone import Subzone
from app.keyboards.admin_items import items_list_keyboard, item_detail_keyboard
from app.keyboards.admin_subzones import subzone_actions_keyboard
from app.utils.db import SessionLocal

item_router = Router()


@item_router.callback_query(F.data.startswith("zone_items:"))
async def zone_items(callback: CallbackQuery):
    await callback.answer()
    zone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        zone = await session.get(Subzone, zone_id)
        result = await session.execute(select(Item).where(Item.subzone_id == zone_id))
        items = result.scalars().all()

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.bot.send_message(
        chat_id=callback.from_user.id,
        text=f"📦 Список предметов в подзоне <b>{zone.title}</b>:",
        reply_markup=items_list_keyboard(zone_id, items),
    )


@item_router.callback_query(F.data.startswith("item_view:"))
async def view_item(callback: CallbackQuery):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        item = await session.get(Item, item_id)

    if not item:
        await callback.message.answer("❗️Предмет не найден.")
        return

    text = f"<b>{item.title}</b>\n\n{item.description}"
    keyboard = item_detail_keyboard(item.id)

    if item.photo:
        await callback.message.answer_photo(
            photo=item.photo,
            caption=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    if item.voice:
        await callback.message.answer_voice(voice=item.voice)

    try:
        await callback.message.delete()
    except:
        pass


@item_router.callback_query(F.data.startswith("item_back:"))
async def back_to_items(callback: CallbackQuery):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        item = await session.get(Item, item_id)
        zone = await session.get(Subzone, item.subzone_id)
        result = await session.execute(select(Item).where(Item.subzone_id == zone.id))
        items = result.scalars().all()

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        f"📦 Список предметов в подзоне <b>{zone.title}</b>:",
        parse_mode="HTML",
        reply_markup=items_list_keyboard(zone.id, items)
    )


@item_router.callback_query(F.data.startswith("subzone_view:"))
async def return_to_zone_card(callback: CallbackQuery):
    await callback.answer()

    parts = callback.data.split(":")
    subzone_id = int(parts[1])
    zone_id = int(parts[2]) if len(parts) > 2 else None

    async with SessionLocal() as session:
        subzone = await session.get(Subzone, subzone_id)
        if not subzone:
            await callback.message.answer("❗️Подзона не найдена.")
            return

        if zone_id is None:
            zone_id = subzone.zone_id

    text = f"<b>{subzone.title}</b>\n\n{subzone.description}"
    keyboard = subzone_actions_keyboard(subzone.id, zone_id)

    try:
        await callback.message.delete()
    except:
        pass

    if subzone.photo:
        await callback.message.answer_photo(
            photo=subzone.photo,
            caption=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    if subzone.voice:
        await callback.message.answer_voice(voice=subzone.voice)
