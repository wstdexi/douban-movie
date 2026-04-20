# 服务层包初始化文件。

from app.services.auth_service import auth_service
from app.services.movie_service import movie_service

__all__ = ["auth_service", "movie_service"]

