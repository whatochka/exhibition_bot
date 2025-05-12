from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from app.models import Subzone, Zone
from app.utils.db import SessionLocal
from app.keyboards.admin_subzones import subzone_actions_keyboard, cancel_keyboard, subzone_list_keyboard
from app.states.subzone import SubzoneEdit

subzone_edit_router = Router()


@subzone_edit_router.callback_query(F.data.startswith("subzone_edit:"))
async def start_zone_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    subzone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        subzone = await session.get(Subzone, subzone_id)
        if not subzone:
            await callback.message.answer("❗ Подзона не найдена.")
            return

    await state.clear()
    await state.set_state(SubzoneEdit.title)
    await state.update_data(
        subzone_id=subzone.id,
        zone_id=subzone.zone_id,
        step="title"
    )

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        "✏️ Введите новое название подзоны:",
        reply_markup=cancel_keyboard()
    )


@subzone_edit_router.message(SubzoneEdit.title)
async def process_title_edit(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(SubzoneEdit.description)
    await message.answer("📝 Введите новое описание подзоны:", reply_markup=cancel_keyboard())


@subzone_edit_router.message(SubzoneEdit.description)
async def process_description_edit(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(SubzoneEdit.image)
    await message.answer("🖼 Отправьте новое фото или напишите <b>нет</b>:", parse_mode="HTML",
                         reply_markup=cancel_keyboard())


@subzone_edit_router.message(SubzoneEdit.image, F.text.casefold() == "нет")
async def skip_image_edit(message: Message, state: FSMContext):
    await state.update_data(photo=None)
    await state.set_state(SubzoneEdit.voice)
    await message.answer("🎤 Отправьте новое голосовое сообщение или напишите <b>нет</b>:", parse_mode="HTML",
                         reply_markup=cancel_keyboard())


@subzone_edit_router.message(SubzoneEdit.image, F.photo)
async def process_image_edit(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(SubzoneEdit.voice)
    await message.answer("🎤 Отправьте новое голосовое сообщение или напишите <b>нет</b>:", parse_mode="HTML",
                         reply_markup=cancel_keyboard())


@subzone_edit_router.message(SubzoneEdit.voice, F.text.casefold() == "нет")
async def skip_voice_edit(message: Message, state: FSMContext):
    await state.update_data(voice=None)
    await finish_zone_edit(message, state)


@subzone_edit_router.message(SubzoneEdit.voice, F.voice)
async def process_voice_edit(message: Message, state: FSMContext):
    await state.update_data(voice=message.voice.file_id)
    await finish_zone_edit(message, state)


@subzone_edit_router.callback_query(F.data == "subzone_cancel")
async def cancel_zone_edit(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    zone_id = data.get("zone_id")
    async with SessionLocal() as session:
        result = await session.execute(select(Subzone).where(Subzone.zone_id == zone_id))
        subzones = result.scalars().all()
    await callback.answer()
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("❌ Редактирование отменено.", reply_markup=subzone_list_keyboard(zone_id, subzones))


async def finish_zone_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    subzone_id = data.get("subzone_id")

    async with SessionLocal() as session:
        subzone = await session.get(Subzone, subzone_id)
        if not subzone:
            await message.answer("❗ Подзона не найдена.")
            return

        zone = await session.get(Zone, subzone.zone_id)
        if not zone:
            await message.answer("❗ Родительская зона не найдена.")
            return

        # Обновление данных
        subzone.title = data.get("title", subzone.title)
        subzone.description = data.get("description", subzone.description)
        subzone.photo = data.get("photo") if data.get("photo") is not None else subzone.photo
        subzone.voice = data.get("voice") if data.get("voice") is not None else subzone.voice

        await session.commit()

        text = f"<b>{subzone.title}</b>\n\n{subzone.description}"
        keyboard = subzone_actions_keyboard(subzone.id, zone.id)

    await state.clear()

    if subzone.photo:
        await message.answer_photo(photo=subzone.photo, caption=text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

    if subzone.voice:
        await message.answer_voice(voice=subzone.voice)

    await state.clear()
