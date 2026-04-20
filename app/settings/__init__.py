# 配置包初始化，统一导出配置对象。
from app.settings.config import Settings, settings

APP_SETTINGS = settings

__all__ = ["Settings", "settings", "APP_SETTINGS"]
