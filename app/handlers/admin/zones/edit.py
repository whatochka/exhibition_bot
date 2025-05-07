from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.models import Zone
from app.utils.db import SessionLocal
from app.keyboards.admin_zones import zone_actions_keyboard, cancel_keyboard

zone_router = Router()


class ZoneEdit(StatesGroup):
    title = State()
    description = State()
    image = State()
    voice = State()


@zone_router.callback_query(F.data.startswith("zone_edit:"))
async def start_zone_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    zone_id = int(callback.data.split(":")[1])
    await state.update_data(zone_id=zone_id)
    await state.set_state(ZoneEdit.title)
    await callback.message.delete()
    await callback.message.answer("✏️ Введите новое название зоны:", reply_markup=cancel_keyboard())


@zone_router.message(ZoneEdit.title)
async def process_title_edit(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(ZoneEdit.description)
    await message.answer("📝 Введите новое описание зоны:", reply_markup=cancel_keyboard())


@zone_router.message(ZoneEdit.description)
async def process_description_edit(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ZoneEdit.image)
    await message.answer("🖼 Отправьте новое фото или напишите <b>нет</b>:", parse_mode="HTML",
                         reply_markup=cancel_keyboard())


@zone_router.message(ZoneEdit.image, F.text.casefold() == "нет")
async def skip_image_edit(message: Message, state: FSMContext):
    await state.update_data(image=None)
    await state.set_state(ZoneEdit.voice)
    await message.answer("🎤 Отправьте новое голосовое сообщение или напишите <b>нет</b>:", parse_mode="HTML",
                         reply_markup=cancel_keyboard())


@zone_router.message(ZoneEdit.image, F.photo)
async def process_image_edit(message: Message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await state.set_state(ZoneEdit.voice)
    await message.answer("🎤 Отправьте новое голосовое сообщение или напишите <b>нет</b>:", parse_mode="HTML",
                         reply_markup=cancel_keyboard())


@zone_router.message(ZoneEdit.voice, F.text.casefold() == "нет")
async def skip_voice_edit(message: Message, state: FSMContext):
    await state.update_data(voice=None)
    await finish_zone_edit(message, state)


@zone_router.message(ZoneEdit.voice, F.voice)
async def process_voice_edit(message: Message, state: FSMContext):
    await state.update_data(voice=message.voice.file_id)
    await finish_zone_edit(message, state)


@zone_router.callback_query(F.data == "item_cancel")
async def cancel_zone_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("❌ Редактирование отменено.")


async def finish_zone_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    zone_id = data.get("zone_id")

    async with SessionLocal() as session:
        zone = await session.get(Zone, zone_id)
        if not zone:
            await message.answer("❗️ Зона не найдена.")
            return

        zone.title = data.get("title")
        zone.description = data.get("description")
        zone.image_path = data.get("image") or zone.image_path
        zone.voice_path = data.get("voice") or zone.voice_path

        await session.commit()

        # Итоговая карточка
        text = f"<b>{zone.title}</b>\n\n{zone.description}"
        try:
            await message.answer_photo(
                photo=zone.image_path,
                caption=text,
                parse_mode="HTML",
                reply_markup=zone_actions_keyboard(zone.id)
            )
        except:
            await message.answer(
                text=text,
                parse_mode="HTML",
                reply_markup=zone_actions_keyboard(zone.id)
            )

        if zone.voice_path:
            await message.answer_voice(voice=zone.voice_path)

    await state.clear()
