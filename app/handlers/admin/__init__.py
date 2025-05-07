from aiogram import Router

from .panel import admin_router as panel_router
from .promote import admin_router as promote_router
from .zones import admin_router as zones_router
from .broadcast import broadcast_router

admin_router = Router()
admin_router.include_router(panel_router)
admin_router.include_router(promote_router)
admin_router.include_router(zones_router)
admin_router.include_router(broadcast_router)
