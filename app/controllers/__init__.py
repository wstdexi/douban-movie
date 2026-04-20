# 控制器包初始化，统一导出控制器模块。
from app.controllers import auth_controller

__all__ = ["auth_controller"]
