from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from app.models import Item
from app.utils.db import SessionLocal
from app.keyboards.admin_items import (
    items_list_keyboard,
    item_cancel_keyboard
)
from app.states.item import ItemCreate


item_create_router = Router()


@item_create_router.callback_query(F.data.startswith("item_create:"))
async def start_create(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    zone_id = int(callback.data.split(":")[1])
    await state.set_state(ItemCreate.title)
    await state.update_data(zone_id=zone_id)
    await callback.message.edit_text("✏️ Введите название предмета:",
                                     reply_markup=item_cancel_keyboard("item_create_cancel"))


@item_create_router.message(ItemCreate.title)
async def create_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(ItemCreate.description)
    await message.answer("📝 Введите описание предмета:", reply_markup=item_cancel_keyboard("item_create_cancel"))


@item_create_router.message(ItemCreate.description)
async def create_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ItemCreate.image)
    await message.answer("🖼 Отправьте изображение или напишите <b>нет</b>:", parse_mode="HTML",
                         reply_markup=item_cancel_keyboard("item_create_cancel"))


@item_create_router.message(ItemCreate.image, F.text.casefold() == "нет")
async def skip_image_create(message: Message, state: FSMContext):
    await state.update_data(image=None)
    await state.set_state(ItemCreate.voice)
    await message.answer("🎤 Отправьте голосовое сообщение или напишите <b>нет</b>:", parse_mode="HTML",
                         reply_markup=item_cancel_keyboard("item_create_cancel"))


@item_create_router.message(ItemCreate.image, F.photo)
async def image_create(message: Message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await state.set_state(ItemCreate.voice)
    await message.answer("🎤 Отправьте голосовое сообщение или напишите <b>нет</b>:", parse_mode="HTML",
                         reply_markup=item_cancel_keyboard("item_create_cancel"))


@item_create_router.message(ItemCreate.voice, F.text.casefold() == "нет")
async def skip_voice_create(message: Message, state: FSMContext):
    await state.update_data(voice=None)
    await finish_create(message, state)


async def finish_create(message: Message, state: FSMContext):
    data = await state.get_data()
    async with SessionLocal() as session:
        item = Item(
            subzone_id=data["zone_id"],
            title=data["title"],
            description=data["description"],
            photo=data.get("image"),
            voice=data.get("voice")
        )
        session.add(item)
        await session.commit()
        result = await session.execute(select(Item).where(Item.subzone_id == data["zone_id"]))
        items = result.scalars().all()
    await state.clear()
    await message.answer("✅ Предмет создан!", reply_markup=items_list_keyboard(data["zone_id"], items))


@item_create_router.callback_query(F.data == "item_create_cancel")
async def cancel_create(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    zone_id = data.get("zone_id")
    await state.clear()
    async with SessionLocal() as session:
        result = await session.execute(select(Item).where(Item.subzone_id == zone_id))
        items = result.scalars().all()
    await callback.message.edit_text("❌ Создание предмета отменено.", reply_markup=items_list_keyboard(zone_id, items))
