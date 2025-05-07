from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.models.zone import Zone
from app.models.item import Item


def zones_keyboard(zones: list[Zone], is_admin: bool = False) -> InlineKeyboardMarkup:
    keyboard = []
    for zone in zones:
        keyboard.append([
            InlineKeyboardButton(text=zone.title, callback_data=f"zone_open:{zone.id}")
        ])
    if is_admin:
        keyboard.append([
            InlineKeyboardButton(text="🛠 Админ-панель", callback_data="admin_panel")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def zone_navigation_keyboard(zone_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Предметы", callback_data="user_items")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="user_menu")]
    ])


def items_keyboard(items: list[Item]) -> InlineKeyboardMarkup:
    keyboard = []
    for item in items:
        keyboard.append([
            InlineKeyboardButton(text=item.title, callback_data=f"user_item:{item.id}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="user_items_back")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def user_menu_keyboard(back_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=back_cb)]
    ])
