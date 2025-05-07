from aiogram import Router

from .view import zone_router as view_router
from .delete import zone_router as delete_router
from .create import zone_router as create_router
from .edit import zone_router as edit_router

from app.handlers.admin.items import (
    item_router,
    item_create_router,
    item_edit_router,
    item_delete_router
)

admin_router = Router()
admin_router.include_router(view_router)
admin_router.include_router(delete_router)
admin_router.include_router(create_router)
admin_router.include_router(edit_router)

admin_router.include_router(item_router)
admin_router.include_router(item_create_router)
admin_router.include_router(item_edit_router)
admin_router.include_router(item_delete_router)
