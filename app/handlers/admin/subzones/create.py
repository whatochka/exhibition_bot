from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from app.states.subzone import SubzoneCreate
from app.utils.db import SessionLocal
from app.models.subzone import Subzone
from app.keyboards.admin_subzones import (
    cancel_keyboard,
    back_or_cancel_keyboard,
    subzone_list_keyboard
)

subzone_create_router = Router()


@subzone_create_router.callback_query(F.data.startswith("subzone_add:"))
async def start_zone_add(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    zone_id = int(callback.data.split(":")[1])
    await state.update_data(zone_id=zone_id)
    await state.set_state(SubzoneCreate.title)
    await state.update_data(step="title")
    await callback.message.edit_text("📝 Введите название подзоны:", reply_markup=cancel_keyboard())


@subzone_create_router.message(SubzoneCreate.title)
async def set_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text, step="description")
    await state.set_state(SubzoneCreate.description)
    await message.answer("📝 Введите описание подзоны:", reply_markup=back_or_cancel_keyboard())


@subzone_create_router.message(SubzoneCreate.description)
async def set_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text, step="image")
    await state.set_state(SubzoneCreate.image)
    await message.answer("📷 Отправьте изображение (или напишите 'нет'):", reply_markup=back_or_cancel_keyboard())


@subzone_create_router.message(SubzoneCreate.image)
async def set_image(message: Message, state: FSMContext):
    photo = None
    if message.photo:
        photo = message.photo[-1].file_id
    elif message.text.lower() != "нет":
        await message.answer("❗ Отправьте изображение или напишите 'нет'")
        return

    await state.update_data(photo=photo, step="voice")
    await state.set_state(SubzoneCreate.voice)
    await message.answer("🎙 Отправьте голосовое сообщение (или напишите 'нет'):",
                         reply_markup=back_or_cancel_keyboard())


@subzone_create_router.message(SubzoneCreate.voice)
async def set_voice(message: Message, state: FSMContext):
    voice = None
    if message.voice:
        voice = message.voice.file_id
    elif message.text.lower() != "нет":
        await message.answer("❗ Отправьте голосовое или напишите 'нет'")
        return

    data = await state.get_data()
    async with SessionLocal() as session:
        zone = Subzone(
            title=data["title"],
            description=data["description"],
            photo=data.get("photo"),
            voice=voice,
            zone_id=data["zone_id"]
        )
        session.add(zone)
        await session.commit()

        result = await session.execute(select(Subzone).where(Subzone.zone_id == data["zone_id"]))
        subzones = result.scalars().all()

    await state.clear()
    await message.answer("✅ Подзона создана!", reply_markup=subzone_list_keyboard(data["zone_id"], subzones))


@subzone_create_router.callback_query(F.data == "subzone_back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    step = data.get("step")

    if step == "description":
        await state.set_state(SubzoneCreate.title)
        await state.update_data(step="title")
        await callback.message.edit_text("📝 Введите название подзоны:", reply_markup=cancel_keyboard())

    elif step == "image":
        await state.set_state(SubzoneCreate.description)
        await state.update_data(step="description")
        await callback.message.edit_text("📝 Введите описание подзоны:", reply_markup=back_or_cancel_keyboard())

    elif step == "voice":
        await state.set_state(SubzoneCreate.image)
        await state.update_data(step="image")
        await callback.message.edit_text("📷 Отправьте изображение (или напишите 'нет'):",
                                         reply_markup=back_or_cancel_keyboard())


@subzone_create_router.callback_query(F.data == "subzone_cancel")
async def cancel_zone(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    zone_id = data.get("zone_id")

    async with SessionLocal() as session:
        result = await session.execute(select(Subzone).where(Subzone.zone_id == zone_id))
        subzones = result.scalars().all()

    await state.clear()

    await callback.message.edit_text(
        "🚫 Создание подзоны отменено.",
        reply_markup=subzone_list_keyboard(zone_id, subzones)
    )
