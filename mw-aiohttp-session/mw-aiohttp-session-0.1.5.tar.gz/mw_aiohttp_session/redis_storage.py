'''
copy code from aiohttp-session.redis_storage.py
为适应使用的的框架，有变更以下内容：
1，cookie_name = 'sessionid'
2，redis中key 为 :  session:key 而非 session_key
3，session data 直接存session_mapping
'''
try:
    import aioredis
except ImportError:  # pragma: no cover
    aioredis = None

import uuid
import warnings
import time
try:
    import ujson as json
except ImportError:  # pragma: no cover
    import json

from distutils.version import StrictVersion
from aiohttp_session import AbstractStorage, Session


class RedisStorage(AbstractStorage):
    """Redis storage"""

    # update cookie_name ,max_age=2 days 2018.9.28 for cxh
    def __init__(self, redis_pool, *, cookie_name="sessionid",
                 domain=None, max_age=60*60*48, path='/',
                 secure=None, httponly=True,
                 key_factory=lambda: uuid.uuid4().hex,
                 encoder=json.dumps, decoder=json.loads):
        super().__init__(cookie_name=cookie_name, domain=domain,
                         max_age=max_age, path=path, secure=secure,
                         httponly=httponly,
                         encoder=encoder, decoder=decoder)
        if aioredis is None:
            raise RuntimeError("Please install aioredis")
        if StrictVersion(aioredis.__version__).version < (1, 0):
            raise RuntimeError("aioredis<1.0 is not supported")
        self._key_factory = key_factory
        if isinstance(redis_pool, aioredis.pool.ConnectionsPool):
            warnings.warn(
                "using a pool created with aioredis.create_pool is deprecated"
                "please use a pool created with aioredis.create_redis_pool",
                DeprecationWarning
            )
            redis_pool = aioredis.commands.Redis(redis_pool)
        elif not isinstance(redis_pool, aioredis.commands.Redis):
            raise TypeError("Expexted aioredis.commands.Redis got {}".format(
                    type(redis_pool)))
        self._redis = redis_pool

    def load_cookie(self, request):
        # 如果有jwt，优先判断jwt，避免cookie与jwt不一致
        cookie = request.query.get('jwt')
        # 登入时，jwt == sessionid
        if cookie is None:
            cookie = request.headers.get('Authorization')
            if cookie and cookie.startswith('bearer'):
                cookie = cookie[7:]
            else :
                cookie = super().load_cookie(request)
        return cookie

    async def load_session(self, request):
        cookie = self.load_cookie(request)
        if cookie is None:
            return Session(None, data=None, new=True, max_age=self.max_age)
        else:
            with await self._redis as conn:
                key = str(cookie)
                # update 2018.9.28 for cxh
                data = await conn.get('session:' + key)
                if data is None:
                    return Session(None, data=None,
                                   new=True, max_age=self.max_age)
                data = data.decode('utf-8')
                try:
                    session_data = self._decoder(data)
                    # 确保框架能识别,sessionz的有效，由redis key的exp时间保证，可以忽略created，值取now，是为了框架的age能有效
                    data = {
                         'created':session_data.get('created',int(time.time())),
                         'session': session_data
                    }
                except ValueError:
                    data = None
                return Session(key, data=data, new=False, max_age=self.max_age)

    def _get_session_data(self, session):
        if not session.empty:
            data = {
                'created': session.created,
                'session': session._mapping
            }
        else:
            data = {}
        return data

    async def save_session(self, request, response, session):
        key = session.identity
        if key is None:
            key = self._key_factory()
            self.save_cookie(response, key,
                             max_age=session.max_age)
        else:
            if session.empty:
                self.save_cookie(response, '',
                                 max_age=session.max_age)
            else:
                key = str(key)
                self.save_cookie(response, key,
                                 max_age=session.max_age)
        # 变更存储结构
        data = self._get_session_data(session)
        session_data = data.pop('session')
        data.update(session_data)
        data = self._encoder(data)
        with await self._redis as conn:
            max_age = session.max_age
            expire = max_age if max_age is not None else 0
            # update 2018.9.28 for cxh
            await conn.set('session:' + key, data, expire=expire)
