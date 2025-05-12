from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.models.zone import Zone
from app.models.subzone import Subzone
from app.models.item import Item


def zones_keyboard(zones: list[Zone], is_admin: bool = False) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🚩 Начать", callback_data="zone_open:1")]
    ]
    if is_admin:
        keyboard.append([
            InlineKeyboardButton(text="🛠 Админ-панель", callback_data="admin_panel")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def user_navigation_keyboard(prev_id: int | None, next_id: int | str | None) -> InlineKeyboardMarkup:
    buttons = []
    if prev_id is not None:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"zone_prev:{prev_id}"))
    if next_id is not None:
        buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"zone_next:{next_id}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def subzones_keyboard(subzones: list[Subzone], prev_id: int | None, next_id: int | str | None) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=subzone.title, callback_data=f"user_subzone:{subzone.id}")]
        for subzone in subzones
    ]
    nav_buttons = []
    if prev_id is not None:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"zone_prev:{prev_id}"))
    if next_id is not None:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"zone_next:{next_id}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def items_keyboard(items: list[Item], back_cb: str = "user_items_back") -> InlineKeyboardMarkup:
    keyboard = []
    for item in items:
        cb = f"user_item:{item.id}:{back_cb}"
        keyboard.append([
            InlineKeyboardButton(text=item.title, callback_data=cb)
        ])
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data=back_cb)
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def final_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Меню", callback_data="user_menu")]
    ])


def user_menu_keyboard(back_cb: str = "user_items_back") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=back_cb)]
    ])
