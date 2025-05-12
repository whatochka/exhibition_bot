from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.models.zone import Zone


def zone_list_keyboard(zones: list[Zone]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=zone.title, callback_data=f"zone_view:{zone.id}")]
        for zone in zones
    ]
    buttons.append([InlineKeyboardButton(text="➕ Добавить зону", callback_data="zone_add")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def zone_actions_keyboard(zone_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"zone_edit:{zone_id}")],
#        [InlineKeyboardButton(text="⏩ Подзоны", callback_data=f"zone_items:{zone_id}")],
        [InlineKeyboardButton(text="⏩ Подзоны", callback_data=f"zone_subzones:{zone_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"zone_delete:{zone_id}")],
        [InlineKeyboardButton(text="📎 QR-код", callback_data=f"zone_qr:{zone_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_zones")]
    ])


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="zone_cancel")]
    ])


def back_or_cancel_keyboard(show_back=True) -> InlineKeyboardMarkup:
    buttons = []
    if show_back:
        buttons.append(InlineKeyboardButton(text="🔙 Назад", callback_data="zone_back"))
    buttons.append(InlineKeyboardButton(text="❌ Отмена", callback_data="zone_cancel"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def zone_delete_confirm_keyboard(zone_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"zone_delete_confirm:{zone_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data=f"zone_view:{zone_id}")
        ]
    ])


def qr_back_to_card_keyboard(zone_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад к карточке", callback_data=f"zone_view:{zone_id}")]
    ])


def zone_edit_navigation_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="zone_back"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="zone_cancel")
        ]
    ])


def cancel_item_creation_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="zone_cancel")]
    ])
