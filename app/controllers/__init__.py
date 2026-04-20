# 控制器包初始化，统一导出参数校验控制器。
from app.controllers.auth_controller import auth_request_controller
from app.controllers.movie_controller import movie_request_controller
from app.controllers.user_controller import user_request_controller

__all__ = ["auth_request_controller", "movie_request_controller", "user_request_controller"]
