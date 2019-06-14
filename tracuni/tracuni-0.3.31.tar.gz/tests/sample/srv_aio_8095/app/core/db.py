import logging
import aiozipkin as az
import asyncio
import asyncpg

from app.core.app import Component
from app.core.helper import PrepareError


def db_decorator(func):
    async def wrapper(*args, **kwargs):
        res = await func(*args, **kwargs)
        return res
    return wrapper


class DB(Component):
    def __init__(self, config):
        super(DB, self).__init__()
        dsn = 'postgres://%s:%s@%s:%s/%s' % (
            config['username'],
            config['password'],
            config['host'],
            config['port'],
            config['dbname']
        )
        self.connect_max_attempts = config.get('connect_max_attempts', 10)
        self.connect_retry_delay = config.get('connect_retry_delay', 5)
        self._dsn = dsn
        self.pool = None

    async def _connect(self):
        while True:
            try:
                self.pool = await asyncpg.create_pool(
                    dsn=self._dsn,
                    max_size=self.app.config['system']['pool_max_size'],
                    min_size=self.app.config['system']['pool_min_size'],
                    max_queries=self.app.config['system']['pool_max_queries'],
                    max_inactive_connection_lifetime=(
                        self.app.config['system']['pool_max_inactive_connection_lifetime']
                    ),
                )
            except Exception as e:
                await asyncio.sleep(5)
                logging.error('DB connect error: %s %s' % (self.__class__.__name__, str(e)))
                logging.error('DSN: %s' % self._dsn)
                logging.error('Trying to reconnect to database...')
            else:
                break

    @db_decorator
    async def execute(self, context_span, db_id, sql, *args):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(sql, *args)
            except Exception as e:
                logging.error('DB _execute %s %s error: %s' % (sql, self.__class__.__name__, str(e)))
                res = e
            else:
                res = None
        return context_span, db_id, res

    @db_decorator
    async def query(self, context_span, db_id, sql, *args):
        async with self.pool.acquire() as conn:
            try:
                res = await conn.fetchrow(sql, *args)
            except Exception as e:
                logging.error('DB _query %s %s error: %s' % (sql, self.__class__.__name__, str(e)))
                res = None
        return context_span, db_id, res

    @db_decorator
    async def query_all(self, sql, *args):
        async with self.pool.acquire() as conn:
            try:
                res = await conn.fetch(sql, *args)
            except Exception as e:
                logging.error('DB _query_all %s %s error: %s' % (sql, self.__class__.__name__, str(e)))
                res = None
        return res

    async def prepare(self):
        self.app.log_info('Connecting to %s' % self._dsn)
        for i in range(self.connect_max_attempts):
            try:
                await self._connect()
                self.app.log_info('Connected to %s' % self._dsn)
                return
            except Exception as e:
                self.app.log_err(str(e))
                await asyncio.sleep(self.connect_retry_delay)
        raise PrepareError('Could not connect to %s' % self._dsn)

    async def start(self):
        pass

    async def stop(self):
        self.app.log_info('Disconnecting from %s' % self._dsn)
        await asyncio.sleep(0.3)

    async def ping(self):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute('select 1')
            except Exception as e:
                logging.error('DB _execute ping')
                res = e
            else:
                res = None
        return res
