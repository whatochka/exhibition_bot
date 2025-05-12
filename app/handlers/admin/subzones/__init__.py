from .view import subzone_view_router
from .create import subzone_create_router
from .delete import subzone_delete_router
from .edit import subzone_edit_router


__all__ = [
    "subzone_create_router",
    "subzone_view_router",
    "subzone_delete_router",
    "subzone_edit_router"
]
