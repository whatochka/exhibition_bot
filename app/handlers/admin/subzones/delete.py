from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from app.utils.db import SessionLocal
from app.models.subzone import Subzone
from app.keyboards.admin_subzones import subzone_list_keyboard, subzone_delete_confirm_keyboard

subzone_delete_router = Router()


@subzone_delete_router.callback_query(F.data.startswith("subzone_delete_confirm:"))
async def do_delete_zone(callback: CallbackQuery):
    await callback.answer()

    zone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        zone = await session.get(Subzone, zone_id)
        if zone:
            await session.delete(zone)
            await session.commit()

            result = await session.execute(select(Subzone))
            subzones = result.scalars().all()

            await callback.message.delete()
            await callback.message.bot.send_message(
                chat_id=callback.from_user.id,
                text="🗑 Подзона удалена.",
                reply_markup=subzone_list_keyboard(zone_id, subzones)
            )
        else:
            await callback.answer("❗️Подзона не найдена.", show_alert=True)


@subzone_delete_router.callback_query(
    F.data.startswith("subzone_delete:") & ~F.data.startswith("subzone_delete_confirm:"))
async def confirm_delete_zone(callback: CallbackQuery):
    await callback.answer()

    zone_id = int(callback.data.split(":")[1])

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.bot.send_message(
        chat_id=callback.from_user.id,
        text="❗️Вы уверены, что хотите удалить эту подзону?",
        reply_markup=subzone_delete_confirm_keyboard(zone_id)
    )
