# 认证服务层：封装登录、刷新、当前用户信息等业务逻辑。

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.user_crud import user_core_crud
from app.models.user import User
from app.schemas.login import CredentialsSchema, JWTOut, RegisterSchema
from app.services.token_blacklist import revoke_token
from app.settings import settings
import app.utils.security as security


class AuthService:
    # 注册：创建新用户并返回 token。
    def register(self, db: Session, payload: RegisterSchema) -> JWTOut:
        if user_core_crud.get_by_username(db, payload.username):
            raise ValueError("username already exists")
        if user_core_crud.get_by_email(db, str(payload.email)):
            raise ValueError("email already exists")

        user = user_core_crud.create(
            db,
            obj_in={
                "username": payload.username.strip(),
                "email": str(payload.email),
                "hashed_password": security.get_password_hash(payload.password),
                "is_superuser": False,
                "signature": payload.signature,
            },
        )

        access_payload = security.build_access_payload(user=user)
        refresh_payload = security.build_refresh_payload(user=user)
        access_token = security.create_access_token(data=access_payload)
        refresh_token = security.create_access_token(data=refresh_payload)
        return JWTOut(access_token=access_token, refresh_token=refresh_token)

    # 登录：校验账号密码并签发 token。
    def login(self, db: Session, credentials: CredentialsSchema) -> JWTOut:
        user = security.authenticate_user(
            identifier=credentials.username, password=credentials.password, db=db
        )
        if not user:
            raise ValueError("错误的 用户名/邮箱 或 密码")

        access_payload = security.build_access_payload(user=user)
        refresh_payload = security.build_refresh_payload(user=user)
        access_token = security.create_access_token(data=access_payload)
        refresh_token = security.create_access_token(data=refresh_payload)
        return JWTOut(access_token=access_token, refresh_token=refresh_token)

    # 刷新：使用 refresh token 换取新的 token。
    def refresh(self, db: Session, refresh_token: str) -> JWTOut:
        try:
            payload = jwt.decode(
                refresh_token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                options={"verify_aud": False},
            )
        except JWTError as exc:
            raise ValueError("Invalid refreshToken") from exc

        data = payload.get("data") or {}
        if data.get("tokenType") != "refreshToken":
            raise ValueError("Invalid token type")

        user_id = data.get("userId")
        if not user_id:
            raise ValueError("Invalid token payload")

        user = user_core_crud.get(db, int(user_id))
        if not user:
            raise ValueError("User not found")

        access_payload = security.build_access_payload(user=user)
        refresh_payload = security.build_refresh_payload(user=user)
        access_token = security.create_access_token(data=access_payload)
        new_refresh_token = security.create_access_token(data=refresh_payload)
        return JWTOut(access_token=access_token, refresh_token=new_refresh_token)

    # 获取当前用户（透传）。
    def me(self, current_user: User) -> User:
        return current_user

    # 退出登录：将 access token 标记为失效（进程内黑名单）。
    def logout(self, token: str) -> None:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                options={"verify_aud": False},
            )
        except JWTError as exc:
            raise ValueError("Invalid token") from exc

        exp = payload.get("exp")
        if not isinstance(exp, int):
            raise ValueError("Invalid token payload")
        revoke_token(token, exp)


auth_service = AuthService()

