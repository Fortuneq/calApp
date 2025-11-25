"""
Handlers package initialization

Exports all routers for registration in the main bot
"""
from .start import router as start_router
from .photo import router as photo_router
from .callbacks import router as callbacks_router
from .manual import router as manual_router
from .chat import router as chat_router

__all__ = [
    "start_router",
    "photo_router",
    "callbacks_router",
    "manual_router",
    "chat_router",
]
