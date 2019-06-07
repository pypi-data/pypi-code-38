from api.exceptions import BadRequestError
from api.resources.links import ResourceLink
from datetime import datetime, date
from decimal import Decimal
from django.http.response import HttpResponse
from django.utils.safestring import SafeText
from logging import getLogger
import json


class JSONMixin(object):
    def deserialise(self, data):
        logger = getLogger('podiant.api')

        try:
            return json.loads(data.decode('utf-8'))
        except json.decoder.JSONDecodeError as ex:
            logger.debug('Error parsing JSON request', exc_info=True)
            raise BadRequestError(str(ex.args[0]))

    def _serialise(self, obj):
        if isinstance(obj, (list, tuple)):
            return [
                self._serialise(o)
                for o in obj
            ]

        if isinstance(obj, dict):
            return dict(
                [
                    (
                        key,
                        self._serialise(value)
                    ) for (
                        key,
                        value
                    ) in obj.items()
                ]
            )

        if isinstance(obj, ResourceLink):
            return obj.resolve(self.request)

        if isinstance(obj, SafeText):
            return str(obj)

        if isinstance(obj, Decimal):
            return float(obj)

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        return obj

    def serialise(self, content):
        return json.dumps(
            self._serialise(content),
            indent=2
        )

    def respond(self, content, *args, **kwargs):
        return HttpResponse(
            content=self.serialise(content),
            content_type='application/vnd.api+json',
            *args,
            **kwargs
        )
