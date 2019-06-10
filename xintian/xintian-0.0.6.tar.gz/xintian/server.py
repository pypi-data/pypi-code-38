import asyncio
import datetime

from sanic import Sanic
from sanic.response import json, text
from sanic.exceptions import RequestTimeout, NotFound

from sanic_openapi import swagger_blueprint
from sanic_useragent import SanicUserAgent
from sanic_sentry import SanicSentry
from sanic_compress import Compress
from sanic_cors import CORS

from xintian import load_config
from xintian.utils import CustomHandler, init_jaeger_tracer
from xintian.db import RedisPool, MySQLPool, MongoPool
from xintian.exception import ServerError

config = load_config()
appid = config.get('APP_ID', __name__)
app = Sanic(appid, error_handler=CustomHandler())
app.config = config

app.blueprint(swagger_blueprint)

Compress(app)
SanicUserAgent.init_app(app)
SanicSentry(app)
CORS(app, automatic_options=True, esources={r"/*": {"origins": "*"}})


@app.listener('before_server_start')
async def before_server_start(app, loop):
    queue = asyncio.Queue()
    app.queue = queue
    app.redis_pool = None
    app.mysql_pool = None
    app.mongo_pool = None
    app.trace = None

    # redis
    if 'REDIS_CONFIG' in app.config:
        redis_pool = RedisPool()
        await redis_pool.open(app.config['REDIS_CONFIG'])
        app.redis_pool = redis_pool

    # mysql
    if 'MYSQL_CONFIG' in app.config:
        mysql_pool = MySQLPool()
        await mysql_pool.open(app.config['MYSQL_CONFIG'])
        app.mysql_pool = mysql_pool

    # mongo
    if 'MONGO_CONFIG' in app.config:
        mongo_pool = MongoPool()
        app.mongo_pool = await mongo_pool.open(app.config['MONGO_CONFIG'])

    # Jaeger trace
    app.trace = init_jaeger_tracer(appid, config.get('USE_PROMETHUS_FOR_JAEGER', False))


@app.listener('after_server_start')
async def after_server_start(app, loop):
    pass


@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    app.queue.join()
    if app.redis_pool is not None:
        app.redis_pool.close()
    if app.mongo_pool is not None:
        app.mongo_pool.close()
    if app.mysql_pool is not None:
        app.mysql_pool.close()
        await app.mysql_pool.wait_closed()
    app.trace.close()


@app.exception(RequestTimeout)
def timeout(request, exception):
    return json({'message': 'Request Timeout'}, 408)


@app.exception(NotFound)
def notfound(request, exception):
    return json(
        {'message': 'Requested URL {} not found'.format(request.url)}, 404)


@app.route('/robots.txt')
def robots(request):
    return text('Ignore me.')


@app.route('/favicon.ico')
def favicon(request):
    return text('Ignore me.')


@app.route('/health')
async def health(request):
    """
    For Kubernetes liveness probe，
    """
    try:
        # check redis valid
        if app.redis_pool:
            await app.redis_pool.save('health', 'ok', 1)

        # check mysql valid
        if app.mysql_pool:
            sql = "SELECT 666"
            result = await app.mysql_pool.fetchone(sql)
            if result is None:
                raise ServerError(error='内部错误', code='10500', message="msg")

    except Exception as e:
        raise ServerError(error='内部错误', code='10500', message="msg")

    return json({
        'pong': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': app.config['API_VERSION']
    })


@app.route('/ready')
async def ready(request):
    """
    For Kubernetes readiness probe，
    """
    try:
        # check redis valid.
        if app.redis_pool:
            await app.redis_pool.save('health', 'ok', 1)

        # check mysql valid.
        if app.mysql_pool:
            sql = "SELECT 666"
            result = await app.mysql_pool.fetchone(sql)
            if result is None:
                raise ServerError(error='内部错误', code='10500', message="msg")
    except Exception as e:
        raise ServerError(error='内部错误', code='10500', message="msg")

    return json({
        'pong': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': app.config['API_VERSION']
    })
