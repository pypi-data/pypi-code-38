"""A module with configured adapaters"""

from requests.adapters import HTTPAdapter

_DEFAULT_POOL_SIZE = 1

DEFAULT = HTTPAdapter()


def build(
        min_pool_size=_DEFAULT_POOL_SIZE,
        max_pool_size=_DEFAULT_POOL_SIZE,
        is_blocking=False,
        retry_policy=0):
    """A helper method to build an adapter

    Args:
        min_pool_size (int):    minimum connection pool size
        max_pool_size (int):    maximum connection pool size
        blocking (bool):        if the connection pool is blocking
        retry_policy (Retry):   a retry policy

    Returns:
        An :class:`HTTPAdapter` configured a specified
    """
    return HTTPAdapter(
        pool_connections=min_pool_size,
        pool_maxsize=max_pool_size,
        pool_block=is_blocking,
        max_retries=retry_policy
    )
