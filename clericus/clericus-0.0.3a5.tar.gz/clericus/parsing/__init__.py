from aiohttp import web
from typing import Dict
import json
from .fields import Field, ListField, ErrorField
from .errors import ParseError
from ..errors import ClientError, ErrorList
import datetime
import inspect


class DictParser():
    def __init__(self, settings=None, *args, **kwargs):
        self.settings = settings or {}
        return

    async def _parse_body(self, request):
        try:
            return json.loads(await request.text())
        except Exception as e:
            print(e)
            return {}

    def _getFields(self):
        return {
            f: theField
            for (f, theField) in filter(
                lambda k: isinstance(k[1], Field),
                inspect.getmembers(self),
            )
        }

    async def parse(self, source: Dict):
        parameters = {}
        errors = []
        for name, parameter in self._getFields().items():
            try:
                if (not parameter.optional) and (name not in source):
                    raise ParseError(
                        message="Missing required field: {}".format(name),
                        statusCode=parameter.missingStatusCode,
                    )
                parameters[name] = parameter.parse(
                    source.get(name, parameter.default)
                )
            except Exception as err:
                errors.append(err)
        if errors:
            raise ErrorList(errors)
        return parameters

    def describe(self):
        return {
            key: field.describe()
            for (key, field) in self._getFields().items()
        }


class RequestParser():
    BodyParser = DictParser
    QueryParser = DictParser
    CookiesParser = DictParser
    HeadersParser = DictParser
    UrlParser = DictParser

    def __init__(self, *args, **kwargs):
        self.settings = kwargs.get("settings", None)
        return

    async def _parse_body(self, request):
        try:
            if request.can_read_body:
                return await request.json()
            return None
        except Exception as e:
            print(e)
            raise ParseError(message="Unable to parse body")

    async def parse(self, request):
        parameters = {}
        errors = []

        if self.BodyParser:
            body = (await self._parse_body(request)) or {}
            try:
                parameters.update(await self.BodyParser().parse(body))
            except ErrorList as errs:
                errors += errs.errors

        if self.QueryParser:
            try:
                parameters.update(
                    await self.QueryParser().parse(request.query)
                )
            except ErrorList as errs:
                errors += errs.errors

        if self.HeadersParser:
            try:
                parameters.update(
                    await self.HeadersParser().parse(request.headers)
                )
            except ErrorList as errs:
                errors += errs.errors

        if self.CookiesParser:
            try:
                parameters.update(
                    await self.CookiesParser(settings=self.settings, ).parse(
                        request.cookies
                    )
                )
            except ErrorList as errs:
                errors += errs.errors

        try:
            parameters.update(
                await self.UrlParser(settings=self.settings, ).parse(
                    request.match_info
                )
            )

        except:
            raise ClientError(statusCode=404)

        if errors:
            raise ErrorList(errors)

        return parameters

    def describe(self):
        """
        Return a dictionary of possible parameters to be parsed
        """
        description = {
            "body": self.BodyParser().describe(),
            "url": self.UrlParser().describe(),
            "query": self.QueryParser().describe(),
        }

        for (k, v) in list(description.items()):
            if not v:
                del description[k]

        return description


class ResponseSerializer():
    def __init__(self, *args, **kwargs):
        return

    def _getFields(self):
        return {
            f: self.__getattribute__(f)
            for f in dir(self)
            if isinstance(self.__getattribute__(f), Field)
        }

    async def serialize(
        self,
        result,
        statusCode=200,
        headers=None,
        cookies=None,
        deletedCookies=None,
        dropBody=False,
    ):
        body = {}
        fields = self._getFields()
        for name, resultField in fields.items():

            if hasattr(resultField, "default"):
                value = result.get(name, resultField.default)
            else:
                value = result[name]

            try:
                value = resultField.serialize(value)
            except Exception as e:
                print(e)
                pass

            serializeTo = getattr(resultField, "serializeTo", name) or name
            body[serializeTo] = value

        headers = {k: "; ".join(vs) for k, vs in headers.items()}

        if not dropBody:
            response = web.json_response(
                body,
                status=statusCode,
                headers=headers or {},
            )
        else:
            response = web.Response(
                None,
                status=statusCode,
                headers=headers or {},
            )

        for c in (cookies or {}).values():

            try:
                value = c["value"].decode("utf")
            except:
                value = c["value"]
            response.set_cookie(
                c["name"],
                value,
                secure=c["secure"],
                httponly=c["httpOnly"],
                expires=c.get(
                    "expires",
                    datetime.datetime.utcnow() + datetime.timedelta(days=1)
                )
            )

        for c in (deletedCookies or {}).values():
            response.del_cookie(c["name"], )

        return response

    def describe(self):
        return {
            "body": {
                key: field.describe()
                for (key, field) in self._getFields().items()
            }
        }


class ResponseSerializerWithErrors(ResponseSerializer):
    errors = ListField(ErrorField)