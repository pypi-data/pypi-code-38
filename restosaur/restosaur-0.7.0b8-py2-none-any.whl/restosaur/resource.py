import functools
import logging
import warnings
import urllib

from collections import OrderedDict, defaultdict

from .representations import (  # NOQA
        RepresentationAlreadyRegistered, ValidatorAlreadyRegistered,
        Representation, Validator, UnknownRepresentation,
        match_representation, NoRepresentationFound, NoMoreMediaTypes)
from .utils import (
        join_content_type_with_vnd,
        split_mediatype,
        get_types_to_check)
from . import responses, urltemplate, serializers, deprecation


log = logging.getLogger(__name__)


def _join_ct_vnd(content_type, vnd):
    return join_content_type_with_vnd(content_type, vnd)


def dict_as_text(obj, ctx, depth=0):
    output = u''

    for key, value in obj.items():
        if isinstance(value, dict):
            value = u'\n'+dict_as_text(value, ctx, depth+1)
        output += u'%s%s: %s\n' % (' '*depth*2, key, value)

    return output


def resource_name_from_path(path):
    return urltemplate.remove_parameters(path).strip('/')


class Resource(object):
    def __init__(
            self, api, path, name=None,
            default_content_type='application/json',
            link_model=None, link_name=None):
        self._api = api
        self._path = path
        self._required_parameters = urltemplate.get_parameters(self._path)
        self._callbacks = defaultdict(dict)
        self._registered_methods = set()
        self._name = name or resource_name_from_path(path)
        self._representations = OrderedDict()
        self._validators = OrderedDict()
        self._default_content_type = default_content_type
        self._supported_media_types = defaultdict(set)

        # register "pass-through" validators

        for content_type, serializer in serializers.get_all():
            self.add_validator(content_type=content_type)

        if link_model:
            self._api.register_view(
                    model=link_model, resource=self, view_name=link_name)

        # register aliases for the decorators
        for verb in ('GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'):
            setattr(
                self, verb.lower(), functools.partial(self._decorator, verb))

    def is_callback_registered(self, method, content_type=None):
        content_type = content_type or self._default_content_type
        return method in self._callbacks[content_type]

    def register_method_callback(self, callback, method, content_type=None):
        content_type = content_type or self._default_content_type
        self._callbacks[content_type][method] = callback
        self._registered_methods.add(method)
        self._supported_media_types[method].add(content_type)

    def get_method_supported_mediatypes(self, method):
        return list(self._supported_media_types[method])

    def get_callback(self, method, content_type=None):
        content_type = content_type or self._default_content_type
        return self._callbacks[content_type][method]

    def get_allowed_methods(self):
        return list(self._registered_methods)

    @property
    def default_content_type(self):
        return self._default_content_type

    def _decorator(self, method, accept=None):
        def wrapper(view):
            if self.is_callback_registered(method, content_type=accept):
                raise ValueError(
                        'Method `%s` is already registered' % method)
            self.register_method_callback(
                    view, method=method, content_type=accept)
            return view
        return wrapper

    def _match_representation(self, instance, ctx, accept=None):
        return match_representation(self, ctx, instance, accept=accept)

    def _http_response(self, response):
        content = ''
        content_type = self._default_content_type
        representation = None

        if response.data is not None:
            try:
                representation = self._match_representation(
                        response.data, response.context)
            except NoRepresentationFound:
                if isinstance(response, responses.SuccessfulResponse):
                    return self._http_response(
                        responses.NotAcceptableResponse(
                            response.context, headers=response.headers))
                elif isinstance(response, (
                        responses.ServerErrorResponse,
                        responses.ClientErrorResponse)):
                    # For errors use any representation supported by
                    # server. It is better to provide any information
                    # in any format instead of nothing.
                    # -- RFC7231 (Section 6.5 & 6.6)
                    #
                    # Restosaur will try to match most acceptible
                    # representation.

                    accept = response.context.headers.get('accept')
                    accepting = ['*/*;q=0.1']

                    if accept:
                        media_type, media_subtype = accept.split('/')
                        accepting.insert(0, '%s/*;q=1' % media_type)

                    try:
                        representation = self._match_representation(
                                response.data, response.context,
                                accept=','.join(accepting))
                    except NoRepresentationFound:
                        # return no content and preserve status code
                        pass
                    else:
                        content = representation.transform(
                                    response.context, response.data)
                        content_type = _join_ct_vnd(
                               representation.content_type, representation.vnd)
                else:
                    # return no content and preserve status code
                    pass
            else:
                content = representation.transform(
                                response.context, response.data)
                content_type = _join_ct_vnd(
                       representation.content_type, representation.vnd)

        response.content_type = content_type
        response.representation = representation
        response.content = content
        response.serializer = (
                representation.serializer if representation else None)

        return response

    @property
    def name(self):
        return self._name

    @property
    def api(self):
        return self._api

    @property
    def path(self):
        return self._path

    @property
    def representations(self):
        result = []
        for models in self._representations.values():
            result += models.values()
        return result + self._api.representations

    def get_representations_for(self, model):
        result = []
        model_class = model
        for models in self._representations.values():
            matching_models = filter(
                    lambda x: x[0] == model_class or x[0] is None,
                    models.items())
            result += list(map(lambda x: x[1], matching_models))
        return result + self._api.get_representations_for(model)

    def has_representation_for(self, model, media_type):
        if media_type not in self._representations:
            return self._api.has_representation_for(model, media_type)

        types_to_check = get_types_to_check(model)

        has_resource_repr = any(map(
            lambda x: x in self._representations[media_type],
            types_to_check))

        return (has_resource_repr
                or self._api.has_representation_for(model, media_type))

    def get_representation(self, model, media_type):
        types_to_check = get_types_to_check(model)

        for cls in types_to_check:
            try:
                return self._representations[media_type][cls]
            except KeyError:
                pass
        try:
            return self._api.get_representation(model, media_type)
        except UnknownRepresentation:
            try:
                return self._representations[media_type][None]
            except KeyError:
                raise UnknownRepresentation(
                    'Neither %s nor %s have representation for %s and "%s"' % (
                        self, self._api, model, media_type))

    def link(self, model, name=None):
        """
        Create named link between model and resource
        """
        self._api.link(model=model, resource=self, name=name)

    def linked_model(self, name=None):
        """
        Decorator for linking `self` (the resource) with model
        """
        def register_model(model_class):
            self.link(model_class, name=name)
            return model_class
        return register_model

    def accept(self, media_type=None):
        media_type = media_type or self._default_content_type
        ct, vnd = split_mediatype(media_type)
        return self.validator(content_type=ct, vnd=vnd)

    def representation(self, model=None, media=None, serializer=None):
        def wrapped(func):
            if isinstance(media, (list, tuple)):
                content_types = map(split_mediatype, media)
            else:
                content_types = [split_mediatype(
                    media or self._default_content_type)]

            for ct, v, args in content_types:
                self.add_representation(
                    model=model, vnd=v, content_type=ct, qvalue=args.get('q'),
                    serializer=serializer, _transform_func=func)
            return func
        return wrapped

    def validator(self, vnd=None, content_type=None, serializer=None):
        def wrapped(func):
            self.add_validator(
                    vnd=vnd, content_type=content_type, serializer=serializer,
                    _validator_func=func)
            return func
        return wrapped

    def add_representation(
            self, model=None, vnd=None, content_type=None, qvalue=None,
            serializer=None, _transform_func=None):

        if model is None:
            warnings.warn(
                'Representation for resource %s should be narrowed to '
                'specified model. Starting from v0.9 representation will '
                'require model explicitely.' % self,
                deprecation.RemovedInRestosaur09Warning)
        content_type = content_type or self._default_content_type
        repr_key = _join_ct_vnd(content_type, vnd)

        if (repr_key in self._representations and
                not repr_key == self._default_content_type
                and model in self._representations[repr_key]):
            raise RepresentationAlreadyRegistered(
                    '%s: %s (%s)' % (self._path, repr_key, model))

        if model is None and qvalue is None:
            qvalue = 0.01

        obj = Representation(
                vnd=vnd, content_type=content_type, serializer=serializer,
                _transform_func=_transform_func, qvalue=qvalue)

        self._representations.setdefault(repr_key, {})
        self._representations[repr_key][model] = obj
        return obj

    def add_validator(
            self, vnd=None, content_type=None, serializer=None,
            _validator_func=None):

        content_type = content_type or self._default_content_type
        repr_key = _join_ct_vnd(content_type, vnd)

        if (repr_key in self._validators and
                not repr_key == self._default_content_type):
            raise ValidatorAlreadyRegistered(
                    '%s: %s' % (self._path, repr_key))

        obj = Validator(
                vnd=vnd, content_type=content_type, serializer=serializer,
                _validator_func=_validator_func)

        self._validators[content_type] = obj
        return obj

    def uri(self, context, params=None, query=None, append_query=False):
        assert params is None or isinstance(
                params, dict), "entity.uri() params should be passed as dict"

        params = params or {}

        uri = context.build_absolute_uri(self._path)
        uri = urltemplate.to_url(uri, params)

        final_query = {}

        if append_query:
            final_query.update(context.parameters)

        final_query.update(query or {})

        if final_query:
            uri += '?'+urllib.urlencode(final_query)

        return uri

    def __repr__(self):
        return '<Resource "%s">' % self.path
