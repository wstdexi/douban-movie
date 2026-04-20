from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.route import movie_route
from app.core.middlewares import register_middlewares
from app.log.log import log


def run_migrations() -> None:
    """Apply all pending Alembic migrations."""
    project_root = Path(__file__).resolve().parent.parent
    alembic_ini = project_root / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini))
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(_: FastAPI):
    log.bind(x_request_id="-").info("Running startup migrations...")
    try:
        run_migrations()
        log.bind(x_request_id="-").info("Database schema is up to date.")
    except Exception:
        log.bind(x_request_id="-").exception("Failed to run database migrations.")
        raise
    yield

# 创建fastapi架构
app = FastAPI(title="豆瓣电影 API", version="1.0.0", lifespan=lifespan)
register_middlewares(app)

# 添加电影相关路由
app.include_router(movie_route.router)
app.include_router(auth_router.router)

# 保留这些别名，供 gRPC 服务和脚本复用。
list_movies = movie_route.list_movies
get_movie = movie_route.get_movie
create_movie_api = movie_route.create_movie_api
update_movie_api = movie_route.update_movie_api
delete_movie_api = movie_route.delete_movie_api
clear_movies_api = movie_route.clear_movies_api
export_movies_csv = movie_route.export_movies_csv

# 后端启动入口
if __name__ == "__main__":
    import uvicorn
    print("文档:http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)