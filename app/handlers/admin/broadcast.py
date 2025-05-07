from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
import asyncio

from app.keyboards.admin_panel import cancel_keyboard, confirm_broadcast_keyboard
from app.models.user import User
from app.utils.db import SessionLocal

broadcast_router = Router()


class BroadcastState(StatesGroup):
    writing = State()
    preview = State()


@broadcast_router.callback_query(F.data == "broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BroadcastState.writing)
    await callback.message.edit_text(
        "✏️ Введите текст сообщения для рассылки:\n",
        parse_mode="HTML",
        reply_markup=cancel_keyboard("admin_panel")
    )


@broadcast_router.message(BroadcastState.writing)
async def receive_message_for_broadcast(message: Message, state: FSMContext):
    await state.update_data(content=message.html_text)
    await state.set_state(BroadcastState.preview)
    await message.answer(
        "📢 <b>Предпросмотр сообщения:</b>\n\n" + message.html_text,
        parse_mode="HTML",
        reply_markup=confirm_broadcast_keyboard()
    )


@broadcast_router.callback_query(F.data == "broadcast_confirm")
async def confirm_and_send(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    text = data.get("content")

    async with SessionLocal() as session:
        users = (await session.execute(select(User.id))).scalars().all()

    async def safe_send(user_id):
        try:
            await callback.bot.send_message(user_id, text, parse_mode="HTML")
            return True
        except:
            return False

    results = await asyncio.gather(*(safe_send(uid) for uid in users))
    count = sum(results)

    await state.clear()
    await callback.message.edit_text(f"✅ Сообщение отправлено {count} пользователям.")


@broadcast_router.callback_query(F.data == "broadcast_cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("❌ Рассылка отменена.", reply_markup=cancel_keyboard("admin_panel"))
