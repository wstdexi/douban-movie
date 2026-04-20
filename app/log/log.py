import logging
import sys
import time
from types import FrameType
from typing import cast

from loguru import logger

from app.core.ctx import CTX_X_REQUEST_ID
from app.settings import APP_SETTINGS


def x_request_id_filter(record):
    record["x_request_id"] = CTX_X_REQUEST_ID.get()
    return True


class Logger:
    """输出日志到文件和控制台"""

    def __init__(self):
        log_name = f"Fast_{time.strftime('%Y-%m-%d', time.localtime()).replace('-', '_')}.log"
        log_path = APP_SETTINGS.logs_root / log_name
        self.logger = logger
        self.logger.remove()
        APP_SETTINGS.logs_root.mkdir(parents=True, exist_ok=True)
        self.logger.add(sys.stdout)
        self.logger.add(
            log_path,
            format="{time:YYYY-MM-DD HH:mm:ss} - "
            "{process.name} | "
            "{thread.name} | "
            "<red> {extra[x_request_id]} </red> | "
            "{module}.{function}:{line} - {level} -{message}",
            encoding="utf-8",
            retention="3 days",
            backtrace=True,
            diagnose=True,
            enqueue=True,
            rotation="00:00",
            filter=x_request_id_filter,
        )

    @staticmethod
    def init_config():
        logger_names = ("uvicorn.asgi", "uvicorn.access", "uvicorn")

        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in logger_names:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [InterceptHandler()]

    def get_logger(self):
        return self.logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.bind(x_request_id=CTX_X_REQUEST_ID.get()).opt(
            depth=depth, exception=record.exc_info
        ).log(level, record.getMessage())


Loggers = Logger()
Loggers.init_config()
log = Loggers.get_logger()
