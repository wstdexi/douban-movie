# 业务路由包初始化，统一导出路由模块。
from app.api.v1.route import movie_route

__all__ = ["movie_route"]

