import re
import asyncio
import logging

log = logging.getLogger('silph.ext.database')


class Database(object):
    def __init__(self, redis_url=None, mysql_url=None, arena_url=None, loop=None, encoding='utf8'):
        self.loop = loop or asyncio.get_event_loop()
        self.redis_url = redis_url
        self.mysql_url = mysql_url
        self.arena_url = arena_url
        self._encoding = encoding

    def connect(self):
        connections = []

        if self.redis_url:
            connections.append(self.connect_redis())

        if self.mysql_url:
            connections.append(self.connect_mysql())

        if self.arena_url:
            connections.append(self.connect_arena())

        tasks = asyncio.gather(*connections)
        self.loop.run_until_complete(tasks)

    def close(self):
        closes = []

        if self.mysql_url:
            closes.append(self.mysql.close())

        if self.redis_url:
            self.redis.close()
            closes.append(self.redis.wait_closed())

        tasks = asyncio.gather(*closes)
        self.loop.run_until_complete(tasks)

    async def connect_redis(self):

        import aioredis

        log.debug('Creating Redis instance')

        self.redis = await aioredis.create_redis_pool(
            self.redis_url,
            encoding=self._encoding,
            minsize=5,
            maxsize=25,
        )

    async def connect_mysql(self):

        from asyncqlio import DatabaseInterface
        from silph.models.base import WebTable

        log.debug('Creating Web MySQL instance')

        self.mysql = DatabaseInterface(self.mysql_url)
        await self.mysql.connect()

        log.debug('Binding Web MySQL to ORM')
        self.mysql.bind_tables(WebTable.metadata)

    async def connect_arena(self):

        from asyncqlio import DatabaseInterface
        from silph.models.base import ArenaTable

        log.debug('Creating Arena MySQL instance')

        self.arena = DatabaseInterface(self.arena_url)
        await self.arena.connect()

        log.debug('Binding Arena MySQL to ORM')
        self.mysql.bind_tables(ArenaTable.metadata)


async def database_engine(app):
    default_mysql_url = 'mysql://root:{}@127.0.0.1:3306/silph-web'
    mysql_url = os.environ.get('MYSQL_URL', default_mysql_url)

    default_redis_url = 'redis://127.0.0.1:6379/0'
    redis_url = os.environ.get('REDIS_URL', default_redis_url)

    # Create our Database
    app['db'] = Database(
        mysql_url=mysql_url.format(os.environ.get('DB_PASS', '')),
        redis_url=redis_url,
        loop=app.loop,
    )

    # Connect to our database backend
    await app['db'].connect_mysql()
    await app['db'].connect_redis()

    # Give the loop back to AIOHTTP, when server is done below will run
    yield

    await app['db'].mysql.close()
    app['db'].redis.close()
    await app['db'].redis.wait_closed()
