"""用户管理路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from kk.utils.auth_util import create_access_token, hash_password, verify_password
from fastapi.security import OAuth2PasswordRequestForm
from server.utils.auth_middleware import get_db,get_required_user
from kk.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """注册请求体"""
    username: str = Field(min_length=2, max_length=50, description="用户名")
    password: str = Field(min_length=8, max_length=128, description="密码（至少8位）")


class TokenResponse(BaseModel):
    """登录/注册返回的Token"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    uid: str
    role: str


class UserResponse(BaseModel):
    """ 用户信息 """
    id: int
    username: str
    uid: str
    role: str


auth = APIRouter(prefix="/auth", tags=["autherization"])

# 注册


@auth.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """注册新用户"""
    # 检查用户名是否已存在
    existing = await db.execute(
        select(User).filter(User.username == data.username)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在"
        )
    # 生成uid：用户名+4位随机hex
    import secrets
    uid = f"{data.username}_{secrets.token_hex(2)}"

    # 创建用户
    user = User(
        username=data.username,
        uid=uid,
        password_hash=hash_password(data.password),
        role="user",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 签发 JWT
    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        uid=user.uid,
        role=user.role,
    )


# 登录
@auth.post("/token", response_model=TokenResponse)
async def login(
    from_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """ 登录，获取JWT token """
    # 按 username 查找用户
    result = await db.execute(
        select(User).filter(User.username == from_data.username)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证密码
    if not verify_password(user.password_hash, from_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 签发Token
    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        uid=user.uid,
        role=user.role,
    )


@auth.get("/me", response_model=UserResponse)
async def getme(user:User=Depends(get_required_user)):
    """返回当前登录信息"""
    return UserResponse(
        id=user.id,
        username=user.username,
        uid=user.uid,
        role=user.role,
    )