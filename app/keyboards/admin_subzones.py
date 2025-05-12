from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.models.subzone import Subzone


def subzone_list_keyboard(zone_id: int, subzones: list) -> InlineKeyboardMarkup:
    keyboard = []
    for subzone in subzones:
        keyboard.append([
            InlineKeyboardButton(text=subzone.title, callback_data=f"subzone_view:{subzone.id}:{zone_id}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="➕ Добавить подзону", callback_data=f"subzone_add:{zone_id}")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data=f"zone_view:{zone_id}")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def subzone_actions_keyboard(subzone_id: int, zone_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"subzone_edit:{subzone_id}:{zone_id}")],
        [InlineKeyboardButton(text="📦 Предметы", callback_data=f"zone_items:{subzone_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"subzone_delete:{subzone_id}:{zone_id}")],
        [InlineKeyboardButton(text="📎 QR-код", callback_data=f"subzone_qr:{subzone_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"zone_subzones:{zone_id}")]
    ])


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="subzone_cancel")]
    ])


def back_or_cancel_keyboard(show_back=True) -> InlineKeyboardMarkup:
    buttons = []
    if show_back:
        buttons.append(InlineKeyboardButton(text="🔙 Назад", callback_data="subzone_back"))
    buttons.append(InlineKeyboardButton(text="❌ Отмена", callback_data="subzone_cancel"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def subzone_delete_confirm_keyboard(subzone_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"subzone_delete_confirm:{subzone_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data=f"subzone_view:{subzone_id}")
        ]
    ])


def qr_back_to_card_keyboard(subzone_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад к карточке", callback_data=f"subzone_view:{subzone_id}")]
    ])


def subzone_edit_navigation_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="subzone_back"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="subzone_cancel")
        ]
    ])


def cancel_item_creation_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="subzone_cancel")]
    ])
