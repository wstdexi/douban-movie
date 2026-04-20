import os
from pathlib import Path


def load_env_file(env_path: str = ".env") -> None:
    path = Path(env_path)
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        row = line.strip()
        if not row or row.startswith("#") or "=" not in row:
            continue
        key, value = row.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


class Settings:
    def __init__(self) -> None:
        self.postgres_user = os.getenv("POSTGRES_USER", "douban_user")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "123456")
        self.postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        self.postgres_port = os.getenv("POSTGRES_PORT", "5432")
        self.postgres_db = os.getenv("POSTGRES_DB", "douban")

        self.douban_base_url = "https://movie.douban.com/top250"
        self.douban_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Referer": "https://movie.douban.com/",
        }
        self.default_export_path = Path("doc/movies.csv")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


load_env_file()
settings = Settings()
