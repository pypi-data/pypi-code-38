from aiohttp import web
from aiohttp.web_request import Request

from app.core.handler import BaseHandler
from app.handlers.http_handler import HttpHandler


class HttpRouter(BaseHandler):
    conn = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        transfer = HttpHandler(self)

        # Основные роуты transfer
        self.server.add_route("POST", "/q", transfer.http_in)
        self.server.add_route("POST", "/cb", transfer.callback_in)
        self.server.add_route("POST", "/err", transfer.gen_error)

        self.server.set_error_handler(self.error_handler)

    async def error_handler(self, context_span, request: Request, error: Exception) -> web.Response:
        self.app.log_err(error)
        if isinstance(error, web.HTTPException):
            return error
        try:
            error_code = int(str(error))
        except:
            error_code = 1
        return web.json_response({"code": error_code, "message": self.config['errors'][str(error)]}, status=500)
