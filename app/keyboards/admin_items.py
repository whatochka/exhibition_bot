from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def items_list_keyboard(zone_id: int, items: list) -> InlineKeyboardMarkup:
    keyboard = []
    for item in items:
        keyboard.append([
            InlineKeyboardButton(text=item.title, callback_data=f"item_view:{item.id}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="➕ Добавить предмет", callback_data=f"item_create:{zone_id}")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data=f"subzone_view:{zone_id}")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def item_detail_keyboard(item_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"item_edit:{item_id}"),
            InlineKeyboardButton(text="❌ Удалить", callback_data=f"item_delete:{item_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад к списку", callback_data=f"item_back:{item_id}")
        ]
    ])


def item_cancel_keyboard(callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data=callback)]
    ])


def item_creation_navigation_keyboard(back_cb: str, cancel_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data=back_cb),
            InlineKeyboardButton(text="❌ Отмена", callback_data=cancel_cb)
        ]
    ])
