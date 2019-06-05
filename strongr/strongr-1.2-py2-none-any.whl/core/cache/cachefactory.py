import strongr.core
from strongr.core.cache import RedisCache, LocalCache


def get_cache(*args, **kwargs):
    driver = strongr.core.getCore().config().cache.driver.strip()

    if driver == 'redis':
        return RedisCache(*args, **kwargs)
    elif driver == 'local':
        return LocalCache(*args, **kwargs)
