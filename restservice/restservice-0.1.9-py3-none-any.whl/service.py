import inflection
import logging
from aiohttp.web import middleware, Application, run_app, json_response
from marshmallow.exceptions import ValidationError
from json.decoder import JSONDecodeError
from .handler import RESTHandler


class RESTService(Application):
    Application.config = None

    @middleware
    async def middleware(self, request, handler):
        try:
            if self.config and isinstance(handler, RESTHandler):
                handler.config = self.config
            return await handler(request)
        except Exception as exc:
            status = exc.status if hasattr(exc, 'status') else 400
            if isinstance(exc, (RuntimeError, TypeError, AttributeError, AssertionError, KeyError)):
                logging.exception(exc)
                status = 500
            error = exc.error if hasattr(exc, 'error') else inflection.underscore(type(exc).__name__).upper()
            message = exc.message if hasattr(exc, 'message') else inflection.humanize(error).capitalize() + '.'
            detail = exc.detail if hasattr(exc, 'detail') else None
            if isinstance(exc, ValidationError):
                detail = exc.messages
            elif isinstance(exc, JSONDecodeError):
                detail = exc.msg
            return json_response(status=status, data=dict(error=error, message=message, detail=detail))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = None
        self.middlewares.append(self.middleware)

    def start(self):
        run_app(self)
