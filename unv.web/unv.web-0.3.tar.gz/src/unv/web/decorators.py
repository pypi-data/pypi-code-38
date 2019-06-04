import functools

import ujson as json

from aiohttp import web

from .helpers import render_template


def as_json(f):
    """Return json response from passed dict result."""
    @functools.wraps(f)
    async def wrapper(request, *args, **kwargs):
        result = await f(request, *args, **kwargs)
        return web.json_response(result, dumps=json.dumps)
    return wrapper


def render(
        template_name: str, default_context: dict = None,
        status: int = web.HTTPOk.status_code):
    """Render jinja2 template by given name and custom context processors."""
    default_context = default_context or {}

    def decorator(f):
        @functools.wraps(f)
        async def wrapper(request, *args, **kwargs):
            context = default_context.copy()
            result = await f(request, *args, **kwargs)
            context.update(result)
            return await render_template(
                request, template_name, context, status)
        return wrapper

    return decorator
