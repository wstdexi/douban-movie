# 迁移入口文件，统一暴露数据库初始化函数。
from app.models.system.migration import init_db

__all__ = ["init_db"]
