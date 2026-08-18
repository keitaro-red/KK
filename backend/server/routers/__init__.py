from fastapi import APIRouter

from server.routers.system_router import system
from server.routers.auth_router import auth
from server.routers.chat_router import chat

router = APIRouter()

# 基础系统接口
router.include_router(system)
router.include_router(auth)
router.include_router(chat)