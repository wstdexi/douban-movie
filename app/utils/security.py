from datetime import datetime, timedelta, timezone

from jose import jwt

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.user_controller import user_core_controller
from app.schemas.login import JWTPayload
from app.settings.config import settings
from app.models.user import User


# 密码哈希上下文（bcrypt 为通用选择）。
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 创建登录用户的token
def create_access_token(*, data: JWTPayload):
    payload = data.model_dump().copy()
    # python-jose expects JSON-serializable values; convert datetimes to unix timestamps.
    if isinstance(payload.get("iat"), datetime):
        payload["iat"] = int(payload["iat"].timestamp())
    if isinstance(payload.get("exp"), datetime):
        payload["exp"] = int(payload["exp"].timestamp())
    encoded_jwt = jwt.encode(payload,settings.jwt_secret_key,algorithm=settings.jwt_algorithm)
    return encoded_jwt

# 检查密码是否正确
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 获取哈希密码
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# 校验用户账号密码（username 或 email 均可）。
def authenticate_user(*, identifier: str, password: str, db: Session) -> User | None:
    user = user_core_controller.get_by_identifier(db, identifier)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# 构建访问令牌 Payload（供登录路由调用）。
def build_access_payload(*, user: User) -> JWTPayload:
    now = datetime.now(timezone.utc)
    return JWTPayload(
        data={"userId": user.id, "userName": user.username, "tokenType": "accessToken"},
        iat=now,
        exp=now + timedelta(minutes=settings.access_token_expire_minutes),
    )


# 构建刷新令牌 Payload（供 refresh 路由调用）。
def build_refresh_payload(*, user: User) -> JWTPayload:
    now = datetime.now(timezone.utc)
    return JWTPayload(
        data={"userId": user.id, "userName": user.username, "tokenType": "refreshToken"},
        iat=now,
        exp=now + timedelta(minutes=settings.refresh_token_expire_minutes),
    )