import os
from functools import lru_cache

from .function import LambdaFunction

__path__ = None


@lru_cache(128)
def __getattr__(module) -> LambdaFunction:
    queue = os.getenv(f"TC_{module.upper()}_QUEUE")
    bucket = os.getenv(f"TC_{module.upper()}_BUCKET")
    print(f"Looking for lambda function {module}")
    if not queue:
        raise ImportError(f"Couldn't automatically create LambdaFunction {module}")
    return LambdaFunction(queue, bucket)
