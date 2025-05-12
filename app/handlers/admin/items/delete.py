from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from app.models import Item
from app.utils.db import SessionLocal
from app.keyboards.admin_items import items_list_keyboard

item_delete_router = Router()


@item_delete_router.callback_query(F.data.startswith("item_delete:"))
async def confirm_item_deletion(callback: CallbackQuery):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"item_delete_confirm:{item_id}"),
            InlineKeyboardButton(text="🔙 Отмена", callback_data=f"item_view:{item_id}")
        ]
    ])

    try:
        await callback.message.edit_text(
            text="❗️Вы уверены, что хотите удалить этот предмет?",
            reply_markup=keyboard
        )
    except:
        await callback.message.answer(
            text="❗️Вы уверены, что хотите удалить этот предмет?",
            reply_markup=keyboard
        )
        try:
            await callback.message.delete()
        except:
            pass


@item_delete_router.callback_query(F.data.startswith("item_delete_confirm:"))
async def delete_item(callback: CallbackQuery):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        item = await session.get(Item, item_id)
        zone_id = item.subzone_id
        await session.delete(item)
        await session.commit()
        result = await session.execute(select(Item).where(Item.subzone_id == zone_id))
        items = result.scalars().all()

    try:
        await callback.message.edit_text("🗑 Предмет удалён.", reply_markup=items_list_keyboard(zone_id, items))
    except:
        await callback.message.answer("🗑 Предмет удалён.", reply_markup=items_list_keyboard(zone_id, items))
        try:
            await callback.message.delete()
        except:
            pass