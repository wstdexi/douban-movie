# 服务层包初始化，统一导出服务模块。
from app.services import movie_service

__all__ = ["movie_service"]
