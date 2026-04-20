# 用户参数校验控制器：负责用户相关输入参数校验。


class UserRequestController:
    # 校验登录标识（username/email）与密码。
    def validate_login_input(self, identifier: str, password: str) -> None:
        if not identifier.strip():
            raise ValueError("username/email is required")
        if not password:
            raise ValueError("password is required")

    # 校验刷新令牌是否为空。
    def validate_refresh_token(self, refresh_token: str | None) -> None:
        if not refresh_token:
            raise ValueError("Missing refreshToken")


user_request_controller = UserRequestController()

