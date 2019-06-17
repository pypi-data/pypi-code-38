from aiohttp import web
from .documentation import handleDocumentation
from .method import Method


class Endpoint():
    def __init__(
        self,
        settings=None,
        name: str = None,
        path: str = None,
    ):
        self.settings = settings or {}
        self.Options = self.generateOptionsClass(
            list(self.methods().keys()) + ["options"],
            settings=self.settings,
        )
        self.name = name
        self.path = path

    def methods(self):
        return {
            f.lower(): self.__getattribute__(f)
            for f in dir(self)
            if isinstance(self.__getattribute__(f), Method.__class__)
            and f[0] != "_"
        }

    async def handle(self, request: web.Request) -> web.Response:
        method = self.methods().get(request.method.lower(), None)
        if method:
            return await method(settings=self.settings).handle(request)
        else:
            return await self.methodNotAllowedHandler(method)

    async def methodNotAllowedHandler(self, method):
        return web.json_response(
            {"errors": ["Method not allowed"]},
            status=405,
        )

    async def handleDocumentation(self, request: web.Request) -> web.Response:
        return await handleDocumentation(self)

    def generateOptionsClass(self, methods, settings=None):
        methodString = ", ".join([m.upper() for m in methods])

        settings = settings or {}

        class Options(Method):
            async def process(self, **kwargs):
                self.setHeader("Allow", methodString)

                # CORS
                self.setHeader("Access-Control-Request-Method", methodString)
                return

        return Options
