import asyncio

from sanic import Blueprint, Sanic

from .configuration import settings


__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = [
    'anji_orm_configuration', 'sentry_configuration', 'background_task_configuration',
    'aiohttp_session_configuration', 'jinja_session_configuration',
    'sanic_session_configuration', 'run_background_task'
]

BACKGROND_TASK_LIST = []
anji_orm_configuration = Blueprint('Anji ORM Configuration')  # pylint: disable=invalid-name
sentry_configuration = Blueprint('Sentry Configuration')  # pylint: disable=invalid-name
background_task_configuration = Blueprint('Background Task Configuration')  # pylint: disable=invalid-name
aiohttp_session_configuration = Blueprint('AIOHttp Configuration')  # pylint: disable=invalid-name
jinja_session_configuration = Blueprint('Jinja Configuration')  # pylint: disable=invalid-name
sanic_session_configuration = Blueprint('Sanic-Session Configuration')  # pylint: disable=invalid-name


@sentry_configuration.listener('before_server_start')
async def sentry_check(_app, _loop) -> None:
    import sentry_sdk
    from sentry_sdk.integrations.sanic import SanicIntegration

    if 'SENTRY_DSN' in settings:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            release=settings.VERSION,
            environment=settings.ENVIRONMENT,
            integrations=[SanicIntegration()]
        )


@aiohttp_session_configuration.listener('before_server_start')
async def init_aiohttp_session(sanic_app, _loop) -> None:
    import aiohttp

    session_kwargs = {}
    if not settings.get('VERIFY_SSL', True):
        session_kwargs['connector'] = aiohttp.TCPConnector(verify_ssl=False)
    sanic_app.async_session = aiohttp.ClientSession(**session_kwargs)  # type: ignore


@aiohttp_session_configuration.listener('after_server_stop')
async def close_aiohttp_session(sanic_app, _loop) -> None:
    await sanic_app.async_session.close()


@jinja_session_configuration.listener('before_server_start')
async def jinja_configuration(sanic_app: Sanic, _loop) -> None:
    from sanic_jinja2 import SanicJinja2

    sanic_app.jinja = SanicJinja2(sanic_app, enable_async=True, pkg_name=sanic_app.name)


@anji_orm_configuration.listener('before_server_start')
async def initial_configuration(_app, _loop) -> None:
    from anji_orm import orm_register

    extensions = {}
    if 'ANJI_ORM_FILE_EXTENSION_CONNECTION_STRING' in settings:
        extensions['file'] = settings.ANJI_ORM_FILE_EXTENSION_CONNECTION_STRING

    orm_register.init(
        settings.get('ANJI_ORM_CONNECTION_STRING', 'rethinkdb://'),
        settings.get('ANJI_ORM_POOL_KWARGS', '{}', cast='@json'),
        async_mode=True,
        extensions=extensions
    )
    await orm_register.async_load()


@anji_orm_configuration.listener('after_server_stop')
async def stop_anji_orm(_sanic_app, _loop) -> None:
    from anji_orm import orm_register

    await orm_register.async_close()


def run_background_task(coroutine) -> None:
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    task = loop.create_task(coroutine)
    BACKGROND_TASK_LIST.append(task)


@background_task_configuration.listener('before_server_start')
async def run_background_tasks(sanic_app, _loop: asyncio.AbstractEventLoop) -> None:
    sanic_app.tasks_list = []


@background_task_configuration.listener('before_server_stop')
async def stop_background_tasks(_app, _loop) -> None:
    for task in BACKGROND_TASK_LIST:
        task.cancel()

    await asyncio.wait(BACKGROND_TASK_LIST)


@sanic_session_configuration.middleware('request')
async def add_session_to_request(request):
    # before each request initialize a session
    # using the client's request
    await request.app.session_interface.open(request)


@sanic_session_configuration.middleware('response')
async def save_session(request, response):
    # after each request save the session,
    # pass the response to set client cookies
    await request.app.session_interface.save(request, response)
