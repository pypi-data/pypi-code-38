import json
import datetime
import decimal
import six

from .datastructures import MultiValueDict


__all__ = [
        'JsonSerializer', 'MultiPartFormDataSerializer',
        'default_serializers']


class SerializeDeserializeError(Exception):
    pass


class DeserializationError(SerializeDeserializeError):
    pass


class SerializationError(SerializeDeserializeError):
    pass


class DefaultRestfulEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(str(obj))
        else:
            return super(DefaultRestfulEncoder, self).default(obj)


class DateTimeJsonSerializer(object):
    def dumps(self, obj):
        try:
            return json.dumps(obj, cls=DefaultRestfulEncoder)
        except (TypeError, ValueError) as ex:
            raise SerializationError(ex)

    def loads(self, txt):
        try:
            return json.loads(txt)
        except (TypeError, ValueError) as ex:
            raise DeserializationError(ex)


class JsonSerializer(object):
    def __init__(self):
        self._json = DateTimeJsonSerializer()

    def loads(self, ctx):
        if isinstance(ctx.raw, bytes):
            try:
                return self._json.loads(ctx.raw.decode(ctx.charset))
            except (TypeError, ValueError) as ex:
                raise DeserializationError(ex)
        else:
            try:
                return self._json.loads(ctx.raw)
            except (TypeError, ValueError) as ex:
                raise DeserializationError(ex)

    def dumps(self, ctx, data):
        try:
            return self._json.dumps(data)
        except (TypeError, ValueError) as ex:
            raise SerializationError(ex)


class MultiPartFormDataSerializer(object):
    def loads(self, ctx):
        data = MultiValueDict()
        data.update(ctx.data)
        data.update(ctx.files)
        return data

    def dumps(self, ctx, data):
        raise NotImplementedError


class HTMLSerializer(object):
    def loads(self, ctx):
        return ctx.raw

    def dumps(self, ctx, data):
        try:
            return six.text_type(data)
        except (TypeError, ValueError, UnicodeEncodeError,
                UnicodeDecodeError) as ex:
            raise SerializationError(ex)


class PlainTextSerializer(object):
    def loads(self, ctx):
        return ctx.raw

    def dumps(self, ctx, data):
        try:
            return six.text_type(data)
        except (TypeError, ValueError, UnicodeEncodeError,
                UnicodeDecodeError) as ex:
            raise SerializationError(ex)


class AlreadyRegistered(Exception):
    pass


class SerializersRegistry(object):
    def __init__(self):
        self._serializers = {}

    def _key(self, mimetype):
        return mimetype.lower()

    def __getitem__(self, item):
        return self._serializers[self._key(str(item))]

    def register(self, mimetype, instance):
        key = self._key(mimetype)
        if key in self._serializers:
            raise AlreadyRegistered(key)
        self._serializers[key] = instance

    def mimetypes(self):
        return self._serializers.keys()

    def items(self):
        return self._serializers.items()

    def contains(self, mimetype):
        return self._key(mimetype) in self._serializers


default_serializers = SerializersRegistry()
default_serializers.register(
        'application/json', JsonSerializer())
default_serializers.register(
        'text/html', HTMLSerializer())
default_serializers.register(
        'text/plain', PlainTextSerializer())
default_serializers.register(
        'multipart/form-data', MultiPartFormDataSerializer())


def register(mimetype, serializer):
    default_serializers.register(mimetype, serializer)


def get(mimetype):
    return default_serializers[mimetype]


def get_all():
    return default_serializers.items()
