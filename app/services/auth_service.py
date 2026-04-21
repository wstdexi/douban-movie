# 认证服务层：封装登录、刷新、当前用户信息等业务逻辑。

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.user_crud import user_core_crud
from app.models.user import User
from app.schemas.login import CredentialsSchema, JWTOut
from app.settings import settings
import app.utils.security as security


class AuthService:
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


auth_service = AuthService()

