from aiogram import Router
from .start import router as start_router
from .instagram import router as instagram_router

def get_handlers_router() -> Router:
    main_router = Router()
    main_router.include_router(start_router)
    main_router.include_router(instagram_router)
    return main_router
