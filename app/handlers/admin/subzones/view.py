from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from sqlalchemy import select
from io import BytesIO
import qrcode
from qrcode.image.pil import PilImage

from app.models.zone import Zone
from app.models.subzone import Subzone
from app.config import BOT_USERNAME
from app.utils.db import SessionLocal
from app.keyboards.admin_subzones import (
    subzone_list_keyboard,
    subzone_actions_keyboard,
    qr_back_to_card_keyboard,
)

subzone_view_router = Router()


@subzone_view_router.callback_query(F.data.startswith("zone_subzones:"))
async def zone_subzones(callback: CallbackQuery):
    await callback.answer()
    zone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        zone = await session.get(Zone, zone_id)
        result = await session.execute(select(Subzone).where(Subzone.zone_id == zone_id))
        subzones = result.scalars().all()

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.bot.send_message(
        chat_id=callback.from_user.id,
        text=f"📦 Список подзон в зоне <b>{zone.title}</b>:",
        parse_mode="HTML",
        reply_markup=subzone_list_keyboard(zone_id, subzones),
    )


@subzone_view_router.callback_query(F.data.startswith("subzone_view:"))
async def view_subzone(callback: CallbackQuery):
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
            reply_markup=keyboard,
        )
    else:
        await callback.message.answer(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    if subzone.voice:
        await callback.message.bot.send_voice(
            chat_id=callback.from_user.id,
            voice=subzone.voice,
        )


@subzone_view_router.callback_query(F.data.startswith("subzone_back:"))
async def back_to_subzones(callback: CallbackQuery):
    await callback.answer()
    subzone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        subzone = await session.get(Subzone, subzone_id)
        if not subzone:
            await callback.message.answer("❗️Подзона не найдена.")
            return
        zone = await session.get(Zone, subzone.zone_id)
        result = await session.execute(select(Subzone).where(Subzone.zone_id == zone.id))
        subzones = result.scalars().all()

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        f"📦 Список подзон в зоне <b>{zone.title}</b>:",
        parse_mode="HTML",
        reply_markup=subzone_list_keyboard(zone.id, subzones)
    )


@subzone_view_router.callback_query(F.data.startswith("zone_view:"))
async def return_to_zone_card(callback: CallbackQuery):
    await callback.answer()
    zone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        zone = await session.get(Zone, zone_id)
        result = await session.execute(select(Subzone).where(Subzone.zone_id == zone_id))
        subzones = result.scalars().all()

    if not zone:
        await callback.message.answer("❗️Зона не найдена.")
        return

    text = f"<b>{zone.title}</b>\n\n{zone.description}"
    keyboard = subzone_list_keyboard(zone.id, subzones)

    try:
        await callback.message.delete()
    except:
        pass

    if zone.image_path:
        await callback.message.answer_photo(photo=zone.image_path, caption=text, parse_mode="HTML",
                                            reply_markup=keyboard)
    else:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)

    if zone.voice_path:
        await callback.message.answer_voice(voice=zone.voice_path)


@subzone_view_router.callback_query(F.data.startswith("subzone_qr:"))
async def send_qr_code(callback: CallbackQuery):
    await callback.answer()

    subzone_id = int(callback.data.split(":")[1])
    link = f"https://t.me/{BOT_USERNAME}?start=subzone_{subzone_id}"

    try:
        await callback.message.delete()
    except:
        pass

    qr = qrcode.make(link, image_factory=PilImage)
    buffer = BytesIO()
    qr.save(buffer)
    buffer.seek(0)

    image = BufferedInputFile(buffer.read(), filename=f"subzone_{subzone_id}_qr.png")

    await callback.message.bot.send_document(
        chat_id=callback.from_user.id,
        document=image,
        caption=f"📎 QR-код для подзоны #{subzone_id}\n\n🔗 {link}",
        reply_markup=qr_back_to_card_keyboard(subzone_id),
    )
