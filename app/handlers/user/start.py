from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from app.models.zone import Zone
from app.keyboards.user_menu import zones_keyboard, zone_navigation_keyboard, user_menu_keyboard, items_keyboard
from app.models.item import Item
from app.models.user import User
from app.config import SUPERUSER_ID
from app.utils.db import SessionLocal

user_router = Router()


@user_router.message(F.text.startswith("/start"))
async def user_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    is_admin = False

    async with SessionLocal() as session:
        existing = await session.get(User, user_id)
        if not existing:
            session.add(User(id=user_id, full_name=message.from_user.full_name))
            await session.commit()

        zones = (await session.execute(select(Zone))).scalars().all()
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if user_id == SUPERUSER_ID or (user and user.is_admin):
            is_admin = True

    if len(message.text.split()) > 1:
        payload = message.text.split()[1]
        if payload.startswith("zone_"):
            zone_id = int(payload.replace("zone_", ""))
            await open_zone_deeplink(message, state, zone_id)
            return

    if not zones:
        await message.answer(
            "Выставка еще не готова ;(",
            reply_markup=zones_keyboard(zones, is_admin=is_admin))
        return

    await message.answer(
        "👋 Добро пожаловать на интерактивную выставку!\nВыберите зону для начала:",
        reply_markup=zones_keyboard(zones, is_admin=is_admin)
    )


async def delete_previous_voice(state: FSMContext, bot):
    data = await state.get_data()
    msg_id = data.get("voice_msg_id")
    chat_id = data.get("voice_chat_id")
    if msg_id and chat_id:
        try:
            await bot.delete_message(chat_id, msg_id)
        except:
            pass
        await state.update_data(voice_msg_id=None, voice_chat_id=None)


async def open_zone_deeplink(message: Message, state: FSMContext, zone_id: int):
    async with SessionLocal() as session:
        zone = await session.get(Zone, zone_id)
        if not zone:
            await message.answer("❗️Зона не найдена.")
            return
        await state.update_data(current_zone_id=zone.id)

    text = f"<b>{zone.title}</b>\n\n{zone.description}"
    keyboard = zone_navigation_keyboard(zone.id)

    if zone.image_path:
        await message.answer_photo(photo=zone.image_path, caption=text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

    if zone.voice_path:
        msg = await message.answer_voice(voice=zone.voice_path)
        await state.update_data(voice_msg_id=msg.message_id, voice_chat_id=msg.chat.id)


@user_router.callback_query(F.data.startswith("zone_open:"))
async def open_zone(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_previous_voice(state, callback.bot)
    zone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        zone = await session.get(Zone, zone_id)
        await state.update_data(current_zone_id=zone.id)

    text = f"<b>{zone.title}</b>\n\n{zone.description}"
    keyboard = zone_navigation_keyboard(zone.id)

    if zone.image_path:
        await callback.message.answer_photo(
            photo=zone.image_path,
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

    if zone.voice_path:
        msg = await callback.message.answer_voice(voice=zone.voice_path)
        await state.update_data(voice_msg_id=msg.message_id, voice_chat_id=msg.chat.id)

    try:
        await callback.message.delete()
    except:
        pass


@user_router.callback_query(F.data == "user_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_previous_voice(state, callback.bot)
    user_id = callback.from_user.id
    is_admin = False

    async with SessionLocal() as session:
        zones = (await session.execute(select(Zone))).scalars().all()
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if user_id == SUPERUSER_ID or (user and user.is_admin):
            is_admin = True

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        "📍 Выберите зону для просмотра:",
        reply_markup=zones_keyboard(zones, is_admin=is_admin)
    )


@user_router.callback_query(F.data == "user_items")
async def open_zone_items(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_previous_voice(state, callback.bot)
    data = await state.get_data()
    zone_id = data.get("current_zone_id")
    async with SessionLocal() as session:
        items = (await session.execute(select(Item).where(Item.zone_id == zone_id))).scalars().all()

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        text="📦 Предметы в этой зоне:",
        reply_markup=items_keyboard(items)
    )


@user_router.callback_query(F.data.startswith("user_item:"))
async def open_item(callback: CallbackQuery):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])
    async with SessionLocal() as session:
        item = await session.get(Item, item_id)

    text = f"<b>{item.title}</b>\n\n{item.description}"
    keyboard = user_menu_keyboard("user_items")

    if item.photo:
        await callback.message.answer_photo(photo=item.photo, caption=text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)

    if item.voice:
        await callback.message.answer_voice(voice=item.voice)

    try:
        await callback.message.delete()
    except:
        pass


@user_router.callback_query(F.data == "user_items_back")
async def back_to_zone(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_previous_voice(state, callback.bot)
    data = await state.get_data()
    zone_id = data.get("current_zone_id")

    async with SessionLocal() as session:
        zone = await session.get(Zone, zone_id)

    text = f"<b>{zone.title}</b>\n\n{zone.description}"
    keyboard = zone_navigation_keyboard(zone.id)

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
        msg = await callback.message.answer_voice(voice=zone.voice_path)
        await state.update_data(voice_msg_id=msg.message_id, voice_chat_id=msg.chat.id)
