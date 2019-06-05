import strongr.core
from strongr.core.lock.file import FileLock
from strongr.core.lock.redis import RedisLock


def get_lock(*args, **kwargs):
    driver = strongr.core.getCore().config().lock.driver.strip()

    # pass config vars to lock constructor
    if hasattr(strongr.core.getCore().config().lock, driver):
        if kwargs is None:
            kwargs = {}
        kwargs.update(getattr(strongr.core.getCore().config().lock, driver).as_dict())

    if driver == 'redis':
        return RedisLock(*args, **kwargs)
    elif driver == 'file':
        return FileLock(*args, **kwargs)
