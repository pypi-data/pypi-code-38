from ..parsing import RequestParser, ResponseSerializer
from aiohttp import web
from typing import ClassVar
import traceback
from inspect import getdoc
from .documentation import handleDocumentation
from ..errors import HTTPError, ClientError
import traceback
import inspect


class Method():
    def __init__(
        self,
        settings=None,
        statusCode=200,
        headers=None,
        cookies=None,
        deletedCookies=None,
    ):
        self.statusCode = statusCode
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.deletedCookies = deletedCookies or {}
        self.settings = settings or {}

    class Parser(RequestParser):
        pass

    class Serializer(ResponseSerializer):
        pass

    async def parse(self, request):
        return await self.Parser(settings=self.settings).parse(request)

    async def process(self, **kwargs):
        return {}

    async def serialize(self, result):
        return await self.Serializer().serialize(
            result,
            statusCode=self.statusCode,
            headers=self.headers,
            cookies=self.cookies,
            deletedCookies=self.deletedCookies,
        )

    def setCookie(
        self,
        name,
        value,
        secure=False,
        httpOnly=False,
        expires=None,
    ):
        self.cookies[name] = {
            "name": name,
            "value": value,
            "secure": secure,
            "httpOnly": httpOnly,
            "expires": expires,
        }

    def unsetCookie(
        self,
        name,
    ):
        self.deletedCookies[name] = {
            "name": name,
        }

    def setHeader(self, name, value):
        if name in self.headers:
            self.headers[name].append(value)
        else:
            self.headers[name] = [value]

    async def handle(self, request: web.Request) -> web.Response:
        try:
            parsedData = await self.parse(request)
            parameters = inspect.signature(self.process).parameters
            if "currentUser" in parameters:
                # if the process function wants the current user, fill it
                # in from the authentication middleware
                currentUser = getattr(
                    request,
                    "currentUser",
                    None,
                )
                if all([
                    currentUser == None,
                    parameters["currentUser"].default ==
                    inspect.Parameter.empty,
                ]):
                    raise ClientError(
                        statusCode=401,
                        message="Unauthorized",
                        errorType="AuthenticationError",
                    )

                parsedData["currentUser"] = currentUser
            result = await self.process(**parsedData)
            return await self.serialize(result, )
        except HTTPError as e:
            return web.json_response(
                {"errors": [e.toJSON()]},
                status=e.statusCode,
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return web.json_response(
                {
                    "errors": [{
                        "message": "Server Error",
                        "errorType": "Unknown",
                    }]
                },
                status=500,
            )

    def describe(self):
        return {
            "description": getdoc(self),
            "request": self.Parser().describe(),
            "response": self.Serializer().describe(),
        }


class Endpoint():
    def __init__(self, settings=None):
        self.settings = settings or {}
        self.Options = self.generateOptionsClass(
            list(self.methods().keys()) + ["options"],
            settings=self.settings,
        )

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
