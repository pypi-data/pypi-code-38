from guillotina import app_settings
from guillotina.utils import get_dotted_name

import logging


logger = logging.getLogger('guillotina_statsd')


class Middleware:

    def __init__(self, app, handler):
        self._client = app_settings['statsd_client']
        self._app = app
        self._handler = handler
        self._prefix = app_settings['statsd'].get(
            'key_prefix', 'guillotina_request')

    async def __call__(self, request):
        timer_key = f'{self._prefix}.processing'
        resp = await self._handler(request)
        try:
            duration_sec = request.events['finish'] - request.events['start']
            duration_msec = int(round(duration_sec * 1000))
            self._client.send_timer(timer_key, duration_msec)
        except (AttributeError, KeyError):
            pass

        try:
            try:
                try:
                    view_name = get_dotted_name(request.found_view.view_func)
                except AttributeError:
                    view_name = get_dotted_name(request.found_view)
            except AttributeError:
                view_name = 'unknown'

            key = f"{self._prefix}.{view_name}"
            self._client.incr(f".{key}.request")
            self._client.incr(f".{key}.{request.method}")
            self._client.incr(f".{key}.{resp.status}")
            self._client.send_timer(f".{key}.{request.method}", duration_msec)
        except:
            logger.warn('Error instrumenting code for statsd...', exc_info=True)

        return resp


async def middleware_factory(app, handler):

    if 'statsd_client' not in app_settings:
        return handler

    return Middleware(app, handler)
