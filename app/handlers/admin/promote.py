from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from app.models.user import User
from app.utils.db import SessionLocal
from app.states.promote import PromoteAdmin
from app.keyboards.admin_panel import build_admin_panel_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_router = Router()


@admin_router.callback_query(F.data == "admin_add")
async def ask_user_id(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
    ])
    await callback.message.edit_text(
        "🆔 Введите Telegram ID пользователя, которого хотите назначить админом:",
        reply_markup=keyboard
    )

    await state.set_state(PromoteAdmin.waiting_for_user_id)


@admin_router.message(PromoteAdmin.waiting_for_user_id, F.text.regexp(r"^\d+$"))
async def process_user_id(message: Message, state: FSMContext):
    user_id = int(message.text)

    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            await message.answer("❌ Пользователь с таким ID не найден в базе.")
        elif user.is_admin:
            await message.answer("⚠️ Этот пользователь уже является админом.")
        else:
            user.is_admin = True
            session.add(user)
            await session.commit()
            await message.answer(f"✅ Пользователь <code>{user_id}</code> теперь админ.")

    await state.clear()
    await message.answer("⚙️ Админ-панель", reply_markup=build_admin_panel_keyboard())
