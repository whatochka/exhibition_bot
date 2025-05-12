from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from app.models import Item
from app.utils.db import SessionLocal
from app.keyboards.admin_items import (
    items_list_keyboard,
    item_detail_keyboard,
    item_cancel_keyboard
)

item_edit_router = Router()


class ItemEdit(StatesGroup):
    title = State()
    description = State()
    photo = State()
    voice = State()


@item_edit_router.callback_query(F.data.startswith("item_edit:"))
async def start_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        item = await session.get(Item, item_id)
        if not item:
            await callback.message.answer("❗️Предмет не найден.")
            return

    await state.set_state(ItemEdit.title)
    await state.update_data(item_id=item_id, zone_id=item.id, step="title")

    try:
        await callback.message.edit_text("✏️ Введите новое название предмета:",
                                         reply_markup=item_cancel_keyboard("item_edit_cancel"))
    except:
        await callback.message.answer("✏️ Введите новое название предмета:",
                                      reply_markup=item_cancel_keyboard("item_edit_cancel"))
        try:
            await callback.message.delete()
        except:
            pass


@item_edit_router.message(ItemEdit.title)
async def set_new_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text, step="description")
    await state.set_state(ItemEdit.description)
    await message.answer("📝 Введите новое описание предмета:", reply_markup=item_cancel_keyboard("item_edit_cancel"))


@item_edit_router.message(ItemEdit.description)
async def set_new_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text, step="photo")
    await state.set_state(ItemEdit.photo)
    await message.answer("🖼 Отправьте новое изображение (или напишите 'нет'):",
                         reply_markup=item_cancel_keyboard("item_edit_cancel"))


@item_edit_router.message(ItemEdit.photo)
async def set_new_photo(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(photo=message.photo[-1].file_id, step="voice")
    elif message.text.lower() == "нет":
        await state.update_data(photo=None, step="voice")
    else:
        await message.answer("❗ Отправьте фото или напишите 'нет'")
        return

    await state.set_state(ItemEdit.voice)
    await message.answer("🎤 Отправьте новое голосовое сообщение (или напишите 'нет'):",
                         reply_markup=item_cancel_keyboard("item_edit_cancel"))


@item_edit_router.message(ItemEdit.voice)
async def set_new_voice(message: Message, state: FSMContext):
    if message.voice:
        await state.update_data(voice=message.voice.file_id)
    elif message.text.lower() == "нет":
        await state.update_data(voice=None)
    else:
        await message.answer("❗ Отправьте голосовое сообщение или напишите 'нет'")
        return

    await finish_edit(message, state)


@item_edit_router.callback_query(F.data == "item_edit_cancel")
async def cancel_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    zone_id = data.get("zone_id")
    await state.clear()

    if zone_id:
        async with SessionLocal() as session:
            result = await session.execute(select(Item).where(Item.id == zone_id))
            items = result.scalars().all()

        try:
            await callback.message.edit_text(
                "🚫 Редактирование предмета отменено.",
                reply_markup=items_list_keyboard(zone_id, items)
            )
        except:
            await callback.message.answer(
                "🚫 Редактирование предмета отменено.",
                reply_markup=items_list_keyboard(zone_id, items)
            )
            try:
                await callback.message.delete()
            except:
                pass
    else:
        await callback.message.answer("🚫 Редактирование предмета отменено. Возвращаемся в меню.")


async def finish_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    item_id = data.get("item_id")

    async with SessionLocal() as session:
        item = await session.get(Item, item_id)
        if not item:
            await message.answer("❗️Ошибка: предмет не найден.")
            return

        item.title = data.get("title")
        item.description = data.get("description")
        item.photo = data.get("photo") or item.photo
        item.voice = data.get("voice") or item.voice
        await session.commit()

    await state.clear()
    text = f"<b>{item.title}</b>\n\n{item.description}"
    keyboard = item_detail_keyboard(item.id)

    if item.photo:
        await message.answer_photo(photo=item.photo, caption=text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(text=text, parse_mode="HTML", reply_markup=keyboard)

    if item.voice:
        await message.answer_voice(voice=item.voice)
