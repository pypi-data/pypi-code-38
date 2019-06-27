import traceback

from .utils import Collection, join_content_type_with_vnd, force_text
from . import serializers, contentnegotiation


class RepresentationAlreadyRegistered(Exception):
    pass


class UnknownRepresentation(Exception):
    pass


class ValidatorAlreadyRegistered(Exception):
    pass


class NoMoreMediaTypes(Exception):
    pass


class NoRepresentationFound(Exception):
    pass


def _pass_through_trasnform(x, ctx):
    return x


def _pass_through_validation(x, ctx):
    return x


class Representation(object):
    def __init__(
            self, vnd=None, content_type='application/json', qvalue=None,
            serializer=None, _transform_func=None):

        self.qvalue = qvalue if qvalue is not None else 1
        self.serializer = serializer or serializers.get(content_type)
        self.content_type = content_type
        self.vnd = vnd
        self._transform_func = _transform_func or _pass_through_trasnform

    def transform(self, context, obj):
        """
        Renders representation of `obj` as raw content
        """
        if isinstance(obj, Collection):
            items = map(
                lambda x: self._transform_func(x, context), obj.iterable)
            data = {
                    obj.key: list(items),
                    obj.totalcount_key: len(obj.iterable),
                    }
        else:
            data = self._transform_func(obj, context)
        return data

    def serialize(self, context, data):
        return self.serializer.dumps(context, data)

    def render(self, context, obj):
        return self.serialize(context, self.transform(context, obj))

    def media_type(self):
        mt = join_content_type_with_vnd(self.content_type, self.vnd)
        return '%s; q=%s' % (mt, self.qvalue)


class Validator(object):
    def __init__(
            self, vnd=None, content_type='application/json',
            serializer=None, _validator_func=None):

        self.serializer = serializer or serializers.get(content_type)
        self.content_type = content_type
        self.vnd = vnd
        self._validator_func = _validator_func or _pass_through_validation

    def parse(self, context):
        """
        Parses raw representation content and builds object
        """
        return self._validator_func(self.serializer.loads(context), context)


class ExceptionRepresentation(object):
    def __init__(self, ex, tb=None, extra=None):
        super(ExceptionRepresentation, self).__init__()
        self.exc_type = type(ex)
        self.exc_value = ex
        self.tb = tb
        self.extra = extra
        self.status_code = 500


def restosaur_exception_dict_as_text(obj, ctx):
    output = u'\n'.join(
            traceback.format_exception(obj.exc_type, obj.exc_value, obj.tb))
    return output


def restosaur_exception_dict_as_dict(obj, ctx):
    data = {}
    data.update(obj.extra or {})
    data.update({
            'class': str(obj.exc_type),
            'error': force_text(obj.exc_value),
            })

    if obj.tb:
        def stack_trace(x):
            return dict(zip(['file', 'line', 'fn', 'source'], x))
        data['traceback'] = list(
                map(stack_trace, traceback.extract_tb(obj.tb)))

    return data


def match_representation(resource, ctx, instance, accept=None):
    """
    Match representation `resource` (or resource-like) representation
    of `instance`, based on `ctx`. Representations matching may be
    narrowed by `accept` media type.
    """

    # Use "*/*" as default -- RFC 7231 (Section 5.3.2)
    accept = accept or ctx.headers.get('accept') or '*/*'

    exclude = []

    if instance is None:
        model = None
    else:
        model = type(instance)

    representations = resource.get_representations_for(model)

    while True:
        try:
            mediatype = _match_media_type(
                    accept, representations, exclude=exclude)
        except NoMoreMediaTypes:
            break

        if not resource.has_representation_for(model, mediatype):
            if resource.has_representation_for(None, mediatype):
                return resource.get_representation(None, mediatype)
            exclude.append(mediatype)
        else:
            return resource.get_representation(model, mediatype)

    raise NoRepresentationFound(
        '%s has no registered representation handler for `%s`' % (
            model, accept))


def _match_media_type(accept, representations, exclude=None):
    exclude = exclude or []

    def _drop_mt_args(x):
        return x.split(';')[0]

    mediatypes = list(set(filter(
            lambda x: _drop_mt_args(x) not in exclude, map(
                lambda x: x.media_type(), representations))))

    if not mediatypes:
        raise NoMoreMediaTypes

    mediatype = contentnegotiation.best_match(mediatypes, accept)

    if not mediatype:
        raise NoMoreMediaTypes

    return _drop_mt_args(mediatype)
