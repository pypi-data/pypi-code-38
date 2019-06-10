import asyncio_redis
import aiomysql
from motor.motor_asyncio import AsyncIOMotorClient


class RedisPool:
    _pool = None
    redis_dict = None

    async def open(self, conf):
        if not self._pool:
            self.redis_dict = conf
            self._pool = await asyncio_redis.Pool.create(
                host=self.redis_dict['host'],
                port=self.redis_dict['port'],
                poolsize=self.redis_dict['pool_size'],
                password=None if self.redis_dict['password'] in ('', None) else self.redis_dict['password'],
                db=self.redis_dict['db']
            )

        return self._pool

    async def save(self, key, value, expire=15):
        redis_dict = self.redis_dict
        return await self._pool.set(key=redis_dict['namespace'] + ':' + key, value=value, expire=expire)

    async def load(self, key):
        redis_dict = self.redis_dict
        return await self._pool.get(redis_dict['namespace'] + ':' + key)

    async def close(self):
        self._pool.close()


class MySQLPool:
    _pool = None
    mysql_dict = None

    async def open(self, conf):
        if not self._pool:
            self.mysql_dict = conf
            self._pool = await aiomysql.create_pool(
                host=self.mysql_dict['host'],
                port=self.mysql_dict['port'],
                user=self.mysql_dict['user'],
                password=self.mysql_dict['password'],
                db=self.mysql_dict['db'],
                maxsize=5,
                autocommit=True,
                use_unicode=True,
                charset="utf8"
            )

        return self._pool

    async def fetchone(self, query: str, *args):
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, *args)
                return await cur.fetchone()

    async def fetchmany(self, query: str, *args):
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, *args)
                return await cur.fetchmany()

    async def fetchall(self, query: str, *args):
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, *args)
                return await cur.fetchall()

    async def close(self):
        self._pool.close()


class MongoPool:
    _pool = None

    async def open(self, conf):
        if not self._pool:
            self.mongo_dict = conf
            mongo_uri = "mongodb://" + self.mongo_dict['host'] + ":" + str(self.mongo_dict['port']) + "/" + \
                        self.mongo_dict['db']
            self._pool = AsyncIOMotorClient(mongo_uri)[self.mongo_dict['db']]

        return self._pool

    async def close(self):
        self._pool.close()
