"""用户数据处理工具"""
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError

JWT_ALGORITHM = "HS256"     # SHA256
JWT_EXPIRATION = 7*24*60*60  # 7天
_PASSWORD_HASHER = PasswordHasher()


def hash_password(password: str) -> str:
    """对明文密码做 argon2 哈希，返回密文（直接存库）。"""
    return _PASSWORD_HASHER.hash(password)


# $argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$RdescudvJCsgt3ub+b+dWRoJ8U7a9CKXBheCbmGqLb8
# │        │      │          │        │            │
# │        │      │          参数     salt（盐）    hash 本体
# │        │      版本号
# │        变体 id = 混合模式（抗 side-channel + 抗 GPU）
# 算法标识


def verify_password(stored_hash: str, password: str) -> bool:
    """验证明文密码是否与库中哈希匹配。"""
    if not stored_hash.startswith("$argon2"):
        return False
    try:
        return _PASSWORD_HASHER.verify(stored_hash, password)
    except (InvalidHash, VerificationError, VerifyMismatchError):
        return False


def _get_jwt_secert() -> str:
    """获取 JWT 前面密钥"""
    secret = os.getenv("JWT_SECRET_KEY", "").strip()
    if secret:
        return secret

    if os.getenv("KK_ENV", "development") in ("prod", "production"):
        raise ValueError("生产环境必须设置 JWT_SECRET_KEY")

    fallback = secrets.token_hex(32)
    os.environ["JWT_SECRET_KEY"] = fallback
    print("⚠ JWT_SECRET_KEY 未配置，已生成临时密钥（重启后失效）")
    return fallback


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """签发JWT。data 必须包含 "sub"（用户ID）"""
    payload = data.copy()
    now = datetime.now(tz=timezone.utc)
    # 过期时间
    expire = now+(expires_delta or timedelta(seconds=JWT_EXPIRATION))
    payload.update({
        "exp": expire,      # 过期时间
        "iat": now,         # 签发时间
        "iss": "kk-api"      # 签发者
    })
    return jwt.encode(payload, _get_jwt_secert(), algorithm=JWT_ALGORITHM)

def decode_access_token(token:str)->dict|None:
    """
    解析 JWT,
    return:
    成功:payload dict
    失败:None
    """
    try:
        return jwt.decode(
            token,
            _get_jwt_secert(),
            algorithms=[JWT_ALGORITHM],
            options={"require":["sub","exp","iat"]},
        )
    except (jwt.PyJWTError,ValueError):
        return None
