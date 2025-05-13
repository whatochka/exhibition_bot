from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from app.models.zone import Zone
from app.models.subzone import Subzone
from app.models.item import Item
from app.models.user import User
from app.config import SUPERUSER_ID
from app.utils.db import SessionLocal
from app.keyboards.user_menu import (
    zones_keyboard,
    user_navigation_keyboard,
    subzones_keyboard,
    items_keyboard,
    final_keyboard, user_menu_keyboard
)

user_router = Router()


@user_router.message(F.text.startswith("/start"))
async def user_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, full_name=message.from_user.full_name)
            session.add(user)
            await session.commit()

        zones = (await session.execute(select(Zone).order_by(Zone.id))).scalars().all()
        is_admin = user_id == SUPERUSER_ID or user.is_admin

    if len(message.text.split()) > 1:
        payload = message.text.split()[1]
        if payload.startswith("zone_"):
            zone_id = int(payload.replace("zone_", ""))
            return await open_zone(message, state, zone_id, zones)
        elif payload.startswith("subzone_"):
            subzone_id = int(payload.replace("subzone_", ""))
            return await open_subzone_direct(message, state, subzone_id)

    await message.answer(
        '👋 <b>Добро пожаловать на интерактивную выставку!</b>\n33 года — это вам не шутки. Студенческий союз МИРЭА прошёл огонь, воду и море поточки. Готовы посмотреть, как это было?\n\n'
        '🚩 Чтобы начать это путешествие во времени — подойдите к первой зоне и жмите <b>«Начать»</b>. Не переживайте, обратно вернётесь без машины времени!)',
        reply_markup=zones_keyboard(zones, is_admin=is_admin)
    )


async def open_subzone_direct(message: Message, state: FSMContext, subzone_id: int):
    async with SessionLocal() as session:
        subzone = await session.get(Subzone, subzone_id)
        if not subzone:
            await message.answer("❗️Подзона не найдена.")
            return

        items = (await session.execute(
            select(Item).where(Item.subzone_id == subzone_id)
        )).scalars().all()

    await state.update_data(current_zone_id=subzone.zone_id)
    await state.update_data(current_subzone_id=subzone.id)

    keyboard = items_keyboard(items, back_cb=f"zone_open:{subzone.zone_id}")

    try:
        await message.delete()
    except:
        pass

    if subzone.photo:
        await message.answer_photo(photo=subzone.photo, caption=f"<b>{subzone.title}</b>\n\n{subzone.description}",
                                   parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(text=f"<b>{subzone.title}</b>\n\n{subzone.description}", parse_mode="HTML",
                             reply_markup=keyboard)


@user_router.callback_query(F.data.startswith("zone_open:"))
async def open_zone_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    zone_id = int(callback.data.split(":")[1])
    await open_zone(callback.message, state, zone_id)


async def open_zone(message: Message, state: FSMContext, zone_id: int, zones: list[Zone] = None):
    await state.update_data(current_zone_id=zone_id)
    async with SessionLocal() as session:
        zone = await session.get(Zone, zone_id)
        if not zones:
            zones = (await session.execute(select(Zone).order_by(Zone.id))).scalars().all()
        subzones = (await session.execute(select(Subzone).where(Subzone.zone_id == zone_id))).scalars().all()

    current_index = next((i for i, z in enumerate(zones) if z.id == zone_id), 0)
    total = len(zones)
    prev_id = zones[current_index - 1].id if current_index > 0 else None
    next_id = zones[current_index + 1].id if current_index < total - 1 else "finish"

    text = f"<b>{zone.title}</b>\n\n{zone.description}"
    kb = subzones_keyboard(subzones, prev_id, next_id) if subzones else user_navigation_keyboard(prev_id, next_id)

    try:
        await message.delete()
    except:
        pass  # вдруг сообщение уже удалено

    if zone.image_path:
        await message.answer_photo(photo=zone.image_path, caption=text, parse_mode="HTML", reply_markup=kb)
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=kb)


@user_router.callback_query(F.data.startswith("zone_prev:"))
async def zone_prev(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    prev_id = int(callback.data.split(":")[1])
    await open_zone(callback.message, state, prev_id)


@user_router.callback_query(F.data.startswith("zone_next:"))
async def zone_next(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    next_part = callback.data.split(":")[1]
    if next_part == "finish":
        try:
            await callback.message.delete()
        except:
            pass

        await callback.message.answer(
            "🌟 Спасибо за участие в интерактивной выставке!\nТы только что прошёл 33 года истории Студенческого союза МИРЭА — с афишами, фото, фактами и воспоминаниями. Надеемся, это было интересно, приятно и чуть-чуть по-домашнему 😊",
            reply_markup=final_keyboard()
        )

    else:
        next_id = int(next_part)
        await open_zone(callback.message, state, next_id)


@user_router.callback_query(F.data.startswith("user_subzone:"))
async def open_subzone(callback: CallbackQuery):
    await callback.answer()
    subzone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        subzone = await session.get(Subzone, subzone_id)
        items = (await session.execute(select(Item).where(Item.subzone_id == subzone_id))).scalars().all()

    text = f"<b>{subzone.title}</b>\n\n{subzone.description}"
    kb = items_keyboard(items, back_cb=f"zone_open:{subzone.zone_id}")

    try:
        await callback.message.delete()
    except:
        pass

    if subzone.photo:
        await callback.message.answer_photo(photo=subzone.photo, caption=text, parse_mode="HTML", reply_markup=kb)
    else:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)


@user_router.callback_query(F.data.startswith("user_item:"))
async def open_user_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split(":")
    item_id = int(parts[1])

    async with SessionLocal() as session:
        item = await session.get(Item, item_id)

    if not item:
        await callback.message.answer("❗️Предмет не найден.")
        return

    if item.subzone_id:
        await state.update_data(current_subzone_id=item.subzone_id)

        async with SessionLocal() as session:
            subzone = await session.get(Subzone, item.subzone_id)
            if subzone:
                await state.update_data(current_zone_id=subzone.zone_id)

    text = f"<b>{item.title}</b>\n\n{item.description}"
    keyboard = user_menu_keyboard("user_items_back")

    try:
        await callback.message.delete()
    except:
        pass

    if item.photo:
        await callback.message.answer_photo(photo=item.photo, caption=text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)

    if item.voice:
        await callback.message.answer_voice(voice=item.voice)


@user_router.callback_query(F.data == "user_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    async with SessionLocal() as session:
        zones = (await session.execute(select(Zone).order_by(Zone.id))).scalars().all()
        user = await session.get(User, user_id)
        is_admin = user_id == SUPERUSER_ID or (user and user.is_admin)

    await callback.message.edit_text(
        '🔁 Нажми <b>«Начать»</b>, чтобы пройти выставку ещё раз — вдруг что-то упустил!',
        reply_markup=zones_keyboard(zones, is_admin=is_admin)
    )


@user_router.callback_query(F.data == "user_subzone_back")
async def back_to_subzone(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    subzone_id = data.get("current_subzone_id")

    async with SessionLocal() as session:
        subzone = await session.get(Subzone, subzone_id)
        items = (await session.execute(select(Item).where(Item.subzone_id == subzone_id))).scalars().all()

    await callback.message.edit_text(
        text=f"<b>{subzone.title}</b>\n\n{subzone.description}",
        parse_mode="HTML",
        reply_markup=items_keyboard(items, back_cb="user_zone_back")
    )


@user_router.callback_query(F.data == "user_items_back")
async def user_items_back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    subzone_id = data.get("current_subzone_id")

    if not subzone_id:
        await callback.message.answer("❗️Не удалось определить подзону.")
        return

    async with SessionLocal() as session:
        subzone = await session.get(Subzone, subzone_id)
        if not subzone:
            await callback.message.answer("❗️Подзона не найдена.")
            return

        items = (await session.execute(select(Item).where(Item.subzone_id == subzone_id))).scalars().all()

    text = f"<b>{subzone.title}</b>\n\n{subzone.description}"
    keyboard = items_keyboard(items, back_cb=f"zone_open:{subzone.zone_id}")

    try:
        await callback.message.delete()
    except:
        pass

    if subzone.photo:
        await callback.message.answer_photo(photo=subzone.photo, caption=text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
