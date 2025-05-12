from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from app.states.zone import ZoneCreate
from app.utils.db import SessionLocal
from app.models.zone import Zone
from app.keyboards.admin_zones import (
    cancel_keyboard,
    back_or_cancel_keyboard,
    zone_list_keyboard
)

zone_router = Router()


@zone_router.callback_query(F.data == "zone_add")
async def start_zone_add(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ZoneCreate.title)
    await state.update_data(step="title")
    await callback.message.edit_text("📝 Введите название зоны:", reply_markup=cancel_keyboard())


@zone_router.message(ZoneCreate.title)
async def set_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text, step="description")
    await state.set_state(ZoneCreate.description)
    await message.answer("📝 Введите описание зоны:", reply_markup=back_or_cancel_keyboard())


@zone_router.message(ZoneCreate.description)
async def set_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text, step="image")
    await state.set_state(ZoneCreate.image)
    await message.answer("📷 Отправьте изображение (или напишите 'нет'):", reply_markup=back_or_cancel_keyboard())


@zone_router.message(ZoneCreate.image)
async def set_image(message: Message, state: FSMContext):
    image_path = None
    if message.photo:
        image_path = message.photo[-1].file_id
    elif message.text.lower() != "нет":
        await message.answer("❗ Отправьте изображение или напишите 'нет'")
        return

    await state.update_data(image_path=image_path, step="voice")
    await state.set_state(ZoneCreate.voice)
    await message.answer("🎙 Отправьте голосовое сообщение (или напишите 'нет'):",
                         reply_markup=back_or_cancel_keyboard())


@zone_router.message(ZoneCreate.voice)
async def set_voice(message: Message, state: FSMContext):
    voice_path = None
    if message.voice:
        voice_path = message.voice.file_id
    elif message.text.lower() != "нет":
        await message.answer("❗ Отправьте голосовое или напишите 'нет'")
        return

    data = await state.get_data()
    async with SessionLocal() as session:
        zone = Zone(
            title=data["title"],
            description=data["description"],
            image_path=data.get("image_path"),
            voice_path=voice_path
        )
        session.add(zone)
        await session.commit()

        result = await session.execute(select(Zone))
        zones = result.scalars().all()

    await state.clear()
    await message.answer("✅ Зона создана!", reply_markup=zone_list_keyboard(zones))


@zone_router.callback_query(F.data == "zone_back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    step = data.get("step")

    if step == "description":
        await state.set_state(ZoneCreate.title)
        await state.update_data(step="title")
        await callback.message.edit_text("📝 Введите название зоны:", reply_markup=cancel_keyboard())

    elif step == "image":
        await state.set_state(ZoneCreate.description)
        await state.update_data(step="description")
        await callback.message.edit_text("📝 Введите описание зоны:", reply_markup=back_or_cancel_keyboard())

    elif step == "voice":
        await state.set_state(ZoneCreate.image)
        await state.update_data(step="image")
        await callback.message.edit_text("📷 Отправьте изображение (или напишите 'нет'):",
                                         reply_markup=back_or_cancel_keyboard())


@zone_router.callback_query(F.data == "zone_cancel")
async def cancel_zone(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    async with SessionLocal() as session:
        result = await session.execute(select(Zone))
        zones = result.scalars().all()

    await callback.message.edit_text("🚫 Создание зоны отменено.", reply_markup=zone_list_keyboard(zones))
