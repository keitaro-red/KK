"""用户管理中间件"""
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kk.models.user import User
from kk.storage.postgres.manager import pg_manager
from kk.utils.auth_util import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token", auto_error=False)


async def get_db():
    """提供数据库会话"""
    async with pg_manager.get_session() as db:
        yield db


async def get_current_user(
    authorization: str | None = Header(None),
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """从JWT 解析当前用户。未登录返回None"""
    if authorization is None:
        return None
    if not authorization.startswith("Bearer "):
        return None

    token = authorization.removeprefix("Bearer ")
    if not token:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    result = await db.execute(
        select(User).filter(User.id == int(user_id))
    )
    return result.scalar_one_or_none()


async def get_required_user(
        user: User | None = Depends(get_current_user),
) -> User:
    """返回登录的用户,要求必须登录，否则返回401"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user
