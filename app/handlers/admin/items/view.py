from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from app.models.item import Item
from app.models.zone import Zone
from app.keyboards.admin_items import items_list_keyboard, item_detail_keyboard
from app.keyboards.admin_zones import zone_actions_keyboard
from app.utils.db import SessionLocal

item_router = Router()


@item_router.callback_query(F.data.startswith("zone_items:"))
async def show_items(callback: CallbackQuery):
    zone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        zone = await session.get(Zone, zone_id)
        items = (await session.execute(select(Item).where(Item.zone_id == zone_id))).scalars().all()

    await callback.message.edit_text(
        text=f"📦 Список предметов в зоне <b>{zone.title}</b>:",
        reply_markup=items_list_keyboard(zone_id, items),
        parse_mode="HTML"
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
        zone = await session.get(Zone, item.zone_id)
        result = await session.execute(select(Item).where(Item.zone_id == zone.id))
        items = result.scalars().all()

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        f"📦 Список предметов в зоне <b>{zone.title}</b>:",
        parse_mode="HTML",
        reply_markup=items_list_keyboard(zone.id, items)
    )


@item_router.callback_query(F.data.startswith("zone_view:"))
async def return_to_zone_card(callback: CallbackQuery):
    await callback.answer()
    zone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        zone = await session.get(Zone, zone_id)

    if not zone:
        await callback.message.answer("❗️Зона не найдена.")
        return

    text = f"<b>{zone.title}</b>\n\n{zone.description}"
    keyboard = zone_actions_keyboard(zone.id)

    if zone.image_path:
        await callback.message.answer_photo(photo=zone.image_path, caption=text, parse_mode="HTML",
                                            reply_markup=keyboard)
    else:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)

    if zone.voice_path:
        await callback.message.answer_voice(voice=zone.voice_path)

    try:
        await callback.message.delete()
    except:
        pass
