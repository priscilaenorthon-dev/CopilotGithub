import logging
import time
import functools
from typing import NamedTuple


class Rect(NamedTuple):
    left: int
    top: int
    width: int
    height: int


def setup_logging(debug: bool = False) -> logging.Logger:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        level=level,
    )
    return logging.getLogger("tbh")


def retry(attempts: int = 3, delay_ms: int = 500, exceptions: tuple = (Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < attempts - 1:
                        time.sleep(delay_ms / 1000)
            raise last_exc
        return wrapper
    return decorator
