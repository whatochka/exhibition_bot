from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from sqlalchemy import select
from io import BytesIO
import qrcode
from qrcode.image.pil import PilImage

from app.models.zone import Zone
from app.config import BOT_USERNAME
from app.utils.db import SessionLocal
from app.keyboards.admin_zones import (
    zone_list_keyboard,
    zone_actions_keyboard,
    qr_back_to_card_keyboard,
)

zone_router = Router()


@zone_router.callback_query(F.data == "admin_zones")
async def view_zones(callback: CallbackQuery):
    async with SessionLocal() as session:
        result = await session.execute(select(Zone))
        zones = result.scalars().all()

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.bot.send_message(
        chat_id=callback.from_user.id,
        text="📋 Список зон:",
        reply_markup=zone_list_keyboard(zones),
    )


@zone_router.callback_query(F.data.startswith("zone_view:"))
async def view_zone(callback: CallbackQuery):
    await callback.answer()
    zone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        zone = await session.get(Zone, zone_id)

    if not zone:
        await callback.message.answer("❗️Зона не найдена.")
        return

    text = f"<b>{zone.title}</b>\n\n{zone.description}"
    keyboard = zone_actions_keyboard(zone_id)

    try:
        await callback.message.delete()
    except:
        pass

    if zone.image_path:
        await callback.message.bot.send_photo(
            chat_id=callback.from_user.id,
            photo=zone.image_path,
            caption=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    else:
        await callback.message.bot.send_message(
            chat_id=callback.from_user.id,
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    if zone.voice_path:
        await callback.message.bot.send_voice(
            chat_id=callback.from_user.id,
            voice=zone.voice_path,
        )


@zone_router.callback_query(F.data.startswith("zone_qr:"))
async def send_qr_code(callback: CallbackQuery):
    await callback.answer()

    zone_id = int(callback.data.split(":")[1])
    link = f"https://t.me/{BOT_USERNAME}?start=zone_{zone_id}"

    try:
        await callback.message.delete()
    except:
        pass

    qr = qrcode.make(link, image_factory=PilImage)
    buffer = BytesIO()
    qr.save(buffer)
    buffer.seek(0)

    image = BufferedInputFile(buffer.read(), filename=f"zone_{zone_id}_qr.png")

    await callback.message.bot.send_document(
        chat_id=callback.from_user.id,
        document=image,
        caption=f"📎 QR-код для зоны #{zone_id}\n\n🔗 {link}",
        reply_markup=qr_back_to_card_keyboard(zone_id),
    )


@zone_router.callback_query(F.data.startswith("zone_items:"))
async def zone_items(callback: CallbackQuery):
    from app.keyboards.admin_items import items_list_keyboard
    from app.models.item import Item

    await callback.answer()
    zone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        zone = await session.get(Zone, zone_id)
        result = await session.execute(select(Item).where(Item.zone_id == zone_id))
        items = result.scalars().all()

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.bot.send_message(
        chat_id=callback.from_user.id,
        text=f"📦 Список предметов в зоне <b>{zone.title}</b>:",
        reply_markup=items_list_keyboard(zone_id, items),
    )
