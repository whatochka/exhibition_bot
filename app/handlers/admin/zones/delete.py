from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from app.utils.db import SessionLocal
from app.models.zone import Zone
from app.keyboards.admin_zones import zone_list_keyboard, zone_delete_confirm_keyboard

zone_router = Router()


@zone_router.callback_query(F.data.startswith("zone_delete_confirm:"))
async def do_delete_zone(callback: CallbackQuery):
    await callback.answer()

    zone_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        zone = await session.get(Zone, zone_id)
        if zone:
            await session.delete(zone)
            await session.commit()

            result = await session.execute(select(Zone))
            zones = result.scalars().all()

            await callback.message.delete()
            await callback.message.bot.send_message(
                chat_id=callback.from_user.id,
                text="🗑 Зона удалена.",
                reply_markup=zone_list_keyboard(zones)
            )
        else:
            await callback.answer("❗️Зона не найдена.", show_alert=True)


@zone_router.callback_query(F.data.startswith("zone_delete:") & ~F.data.startswith("zone_delete_confirm:"))
async def confirm_delete_zone(callback: CallbackQuery):
    await callback.answer()

    zone_id = int(callback.data.split(":")[1])

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.bot.send_message(
        chat_id=callback.from_user.id,
        text="❗️Вы уверены, что хотите удалить эту зону?",
        reply_markup=zone_delete_confirm_keyboard(zone_id)
    )
