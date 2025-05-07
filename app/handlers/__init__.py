from .user import user_router
from .admin import admin_router


def register_all_handlers(dp):
    dp.include_router(user_router)
    dp.include_router(admin_router)
