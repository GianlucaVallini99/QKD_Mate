import time
import functools
from typing import Callable, Type

class QKDClientError(Exception): ...

def retry(exceptions: tuple[Type[BaseException], ...], tries: int = 2, delay: float = 0.8):
    def deco(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            for attempt in range(tries):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last = e
                    if attempt == tries - 1:
                        raise
                    time.sleep(delay)
            raise last
        return wrapper
    return deco