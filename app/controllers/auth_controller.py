# 认证参数校验控制器：负责登录与刷新接口的输入校验。

from app.schemas.login import CredentialsSchema


class AuthRequestController:
    # 校验登录输入。
    def validate_login_input(self, credentials: CredentialsSchema) -> None:
        if not credentials.username.strip():
            raise ValueError("username is required")
        if not credentials.password:
            raise ValueError("password is required")

    # 校验刷新令牌输入。
    def validate_refresh_input(self, refresh_token: str | None) -> None:
        if not refresh_token:
            raise ValueError("Missing refreshToken")


auth_request_controller = AuthRequestController()

