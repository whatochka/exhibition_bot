from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from app.config import SUPERUSER_ID
from app.models.user import User
from app.utils.db import SessionLocal
from app.keyboards.admin_panel import build_admin_panel_keyboard

admin_router = Router()


@admin_router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user_id == SUPERUSER_ID:
            if not user:
                user = User(id=user_id, full_name=full_name, is_admin=True)
                session.add(user)
                await session.commit()
        elif not user or not user.is_admin:
            await callback.answer("⛔ У вас нет прав доступа", show_alert=True)
            return

    await callback.message.edit_text("⚙️ Админ-панель", reply_markup=build_admin_panel_keyboard())
