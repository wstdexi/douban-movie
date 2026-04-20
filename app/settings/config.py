from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 数据库配置（字段名你可以保持不变）
    postgres_user: str = "douban_user"
    postgres_password: str = "123456"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_db: str = "douban"

    # 业务配置
    douban_base_url: str = "https://movie.douban.com/top250"
    # 豆瓣请求头（默认值固定，避免被反爬限制）。
    douban_headers: dict[str, str] = Field(
        default_factory=lambda: {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Referer": "https://movie.douban.com/",
        }
    )
    # 默认导出路径（脚本使用）。
    default_export_path: Path = Path("doc/movies.csv")
    logs_root: Path = Path("logs")

    model_config = SettingsConfigDict(
        env_file=".env",          # 自动读 .env
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    jwt_secret_key: str = Field(default="my_key", validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_minutes: int = Field(default=60 * 24 * 7, validation_alias="REFRESH_TOKEN_EXPIRE_MINUTES")
    # 超级用户配置（用于初始化时自动创建）。
    superuser_username: str = Field(default="admin", validation_alias="SUPERUSER_USERNAME")
    superuser_email: str = Field(default="admin@example.com", validation_alias="SUPERUSER_EMAIL")
    # 建议在 .env 中设置该值；为空则跳过创建超级用户。
    superuser_password: str = Field(default="123456", validation_alias="SUPERUSER_PASSWORD")


    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()