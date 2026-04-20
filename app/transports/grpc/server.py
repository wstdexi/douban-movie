from concurrent import futures
import os
import subprocess
import sys
import threading
import time

import grpc
import uvicorn
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError

from app.models.system.migration import init_db
from app.models.system.session import SessionLocal
from app.init_data import crawl_douban_top250, save_movies
from app.models.movies import Movie
from app.transports.grpc.generated import movie_pb2_grpc
from app.transports.grpc.services.movie_grpc_service import MovieService
from app.transports.http.grpc_gateway import app as http_app

DEFAULT_GRPC_ADDR = "0.0.0.0:50051"
DEFAULT_HTTP_ADDR = "0.0.0.0:8000"

_ALEMBIC_INITIAL_REV = "20260417_0001"


def _maybe_run_alembic() -> None:
    flag = os.getenv("RUN_ALEMBIC_UPGRADE", "").strip().lower()
    if flag not in {"1", "true", "yes", "on"}:
        return

    with SessionLocal() as db:
        movie_exists = db.scalar(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'movie'
                )
                """
            )
        )
        alembic_version_exists = db.scalar(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'alembic_version'
                )
                """
            )
        )
        alembic_version_rows = 0
        if alembic_version_exists:
            alembic_version_rows = db.scalar(text("SELECT COUNT(*) FROM alembic_version")) or 0

    # If DB already has the `movie` table from older bootstrap paths, but Alembic isn't
    # tracking the schema yet, stamp the initial revision to avoid "relation already exists"
    # on upgrade.
    if movie_exists and ((not alembic_version_exists) or alembic_version_rows == 0):
        print(f"Alembic: stamping {_ALEMBIC_INITIAL_REV} (existing schema detected)")
        subprocess.run(
            [sys.executable, "-m", "alembic", "stamp", _ALEMBIC_INITIAL_REV],
            check=True,
        )

    print("Alembic: upgrade head")
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)


def bootstrap_data_if_needed(max_retries: int = 30, retry_interval: float = 2.0) -> None:
    for attempt in range(1, max_retries + 1):
        try:
            _maybe_run_alembic()
            init_db()
            with SessionLocal() as db:
                movie_count = db.scalar(select(func.count()).select_from(Movie)) or 0
            if movie_count > 0:
                print(f"跳过初始化：当前已有 {movie_count} 条电影数据。")
                return
            print("检测到空库，开始抓取并初始化电影数据...")
            movies = crawl_douban_top250()
            upserted = save_movies(movies)
            print(f"初始化完成：抓取 {len(movies)} 条，入库/更新 {upserted} 条。")
            return
        except SQLAlchemyError as exc:
            if attempt == max_retries:
                raise RuntimeError(f"数据库在重试后仍不可用: {exc}") from exc
            print(f"等待数据库就绪 ({attempt}/{max_retries})，{retry_interval:.1f}s 后重试: {exc}")
            time.sleep(retry_interval)


def serve(bind_addr: str = DEFAULT_GRPC_ADDR) -> None:
    bootstrap_data_if_needed()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    movie_pb2_grpc.add_MovieServiceServicer_to_server(MovieService(), server)
    server.add_insecure_port(bind_addr)
    server.start()
    print(f"gRPC server listening on {bind_addr}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down gRPC server...")
        server.stop(grace=2)


def wait_for_grpc_ready(target: str, timeout_seconds: float = 60.0) -> None:
    deadline = time.time() + timeout_seconds
    last_err: Exception | None = None
    while time.time() < deadline:
        channel = grpc.insecure_channel(target)
        try:
            grpc.channel_ready_future(channel).result(timeout=2.0)
            return
        except Exception as exc:
            last_err = exc
            time.sleep(0.5)
        finally:
            channel.close()
    raise RuntimeError(f"gRPC not ready at {target} after {timeout_seconds}s: {last_err}")


def main() -> None:
    # HTTP gateway (same container) should call local gRPC server.
    grpc_target = os.environ.setdefault("GRPC_TARGET", "localhost:50051")

    t = threading.Thread(target=serve, name="grpc-server", daemon=True)
    t.start()

    wait_for_grpc_ready(grpc_target)
    uvicorn.run(http_app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
