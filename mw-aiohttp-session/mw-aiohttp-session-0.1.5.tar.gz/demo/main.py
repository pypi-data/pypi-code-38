import asyncio
import aioredis
import time

from aiohttp import web
from aiohttp_session import setup, get_session
# 需使用修改后的RedisStorage，以适用本团队的session 存redis中方式
from mw_aiohttp_session.redis_storage import RedisStorage

async def handler(request):
    session = await get_session(request)
    last_visit = session['last_visit'] if 'last_visit' in session else None
    session['last_visit'] = time.time()
    session.update({"uid": "2222", "uname": "dev", "systemuser": True, "manageuser": False, "manageuserid": None})
    text = 'Last visited: {}'.format(last_visit)
    return web.Response(text=text)
async def say_hello(request):
    return web.Response(text='hello')

async def make_redis_pool():
    redis_address = ('192.168.101.70', '6380')
    return await aioredis.create_redis_pool(redis_address, timeout=1)


def make_app():
    loop = asyncio.get_event_loop()
    redis_pool = loop.run_until_complete(make_redis_pool())
    storage = RedisStorage(redis_pool)

    async def dispose_redis_pool(app):
        redis_pool.close()
        await redis_pool.wait_closed()

    app = web.Application()
    setup(app, storage)
    app.on_cleanup.append(dispose_redis_pool)
    app.router.add_get('/', handler)
    app.router.add_get('/hello',say_hello)
    return app

web.run_app(make_app(),port=8899)


