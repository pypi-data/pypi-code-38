from collections import defaultdict

from .representations import (
        RepresentationAlreadyRegistered, UnknownRepresentation,
        Representation, ExceptionRepresentation,
        restosaur_exception_dict_as_text,
        restosaur_exception_dict_as_dict)
from .resource import Resource
from .utils import join_content_type_with_vnd, get_types_to_check
from .context import Context
from .linking import ModelLinksRegistry


class ModelViewAlreadyRegistered(Exception):
    pass


class ModelViewNotRegistered(Exception):
    pass


class BaseAPI(object):
    def __init__(
            self, path=None, middlewares=None,
            context_class=None, default_charset=None, debug=False):
        path = path or ''
        if path and not path.endswith('/'):
            path += '/'
        if path and path.startswith('/'):
            path = path[1:]
        self.path = path
        self._mimetype_qvalues = {}
        self.debug = debug
        self.resources = []
        self.default_charset = default_charset or 'utf-8'
        self.middlewares = middlewares or []
        self._representations = defaultdict(dict)  # type->repr_key
        self.context_class = context_class or Context
        self.model_links = ModelLinksRegistry()

    def make_context(self, **kwargs):
        return self.context_class(self, **kwargs)

    def add_resources(self, *resources):
        self.resources += resources

    def resource(self, path, *args, **kw):
        obj = Resource(self, path, *args, **kw)
        self.add_resources(obj)
        return obj

    def set_default_qvalue(self, mimetype, qvalue):
        self._mimetype_qvalues[mimetype] = qvalue

    def get_default_qvalue(self, mimetype):
        return self._mimetype_qvalues.get(mimetype)

    def add_representation(
            self, type_, content_type, vnd=None, qvalue=None,
            serializer=None, _transform_func=None):

        if type_ is None and qvalue is None:
            qvalue = 0.01
        elif qvalue is None:
            repr_key = join_content_type_with_vnd(content_type, vnd)
            qvalue = self.get_default_qvalue(repr_key)

        representation = Representation(
            content_type=content_type, vnd=vnd,
            serializer=serializer, _transform_func=_transform_func,
            qvalue=qvalue)

        self.register_representation(type_, representation)

    def register_representation(self, type_, representation):

        content_type = representation.content_type
        vnd = representation.vnd
        repr_key = join_content_type_with_vnd(content_type, vnd)

        if (repr_key in self._representations and
                type_ in self._representations[repr_key]):
            raise RepresentationAlreadyRegistered(
                            '%s for %s' % (repr_key, type_))

        self._representations[repr_key][type_] = representation

    def get_representation(self, model, media_type):
        if media_type not in self._representations:
            raise UnknownRepresentation(
                '%s has no representation for %s and "%s"' % (
                    self, model, media_type))

        types_to_check = get_types_to_check(model)

        for cls in types_to_check:
            try:
                return self._representations[media_type][cls]
            except KeyError:
                pass
        raise UnknownRepresentation(
            '%s has no representation for %s and "%s"' % (
                        self, model, media_type))

    def has_representation_for(self, model, media_type):
        if media_type not in self._representations:
            return False

        types_to_check = get_types_to_check(model)

        return any(map(
            lambda x: x in self._representations[media_type],
            types_to_check))

    @property
    def representations(self):
        result = []
        for models in self._representations.values():
            result += models.values()
        return result

    def get_representations_for(self, model):
        result = []
        model_class = model
        for models in self._representations.values():
            matching_models = filter(
                    lambda x: x[0] is model_class or x[0] is None,
                    models.items())
            result += list(map(lambda x: x[1], matching_models))

        return result

    def linked_resource(self, model, name=None):
        """
        Return linked resource for model instance or class.
        """
        return self.model_links.linked_resource(model=model, name=name)

    def linked_url(
            self, context, instance_or_class, name=None,
            parameters=None, query=None):
        return self.model_links.url(
                context, instance_or_class, name=name,
                parameters=parameters, query=query)

    def link(self, model, resource, name=None):
        self.model_links.link(
                model=model, resource=resource, name=name)

    def model_for(self, resource, name=None):
        """
        A shortcut decorator for linking model between resource.

        The `resource` may be passed as a dotted string path
        to avoid circular import problems.
        """

        def register_link_for_model(model):
            self.link(model=model, resource=resource, name=name)
            return model
        return register_link_for_model


class API(BaseAPI):
    def __init__(self, *args, **kw):
        super(API, self).__init__(*args, **kw)

        # backward compatibility
        configure_plain_text_api(self)
        configure_json_api(self)


JSON = API


def configure_json_api(api):
    api.add_representation(
            ExceptionRepresentation, content_type='application/json',
            _transform_func=restosaur_exception_dict_as_dict,
            qvalue=0.9)
    api.add_representation(
            dict, content_type='application/json',
            qvalue=0.1)

    # backward compatibility

    from .utils import Collection
    api.add_representation(
            Collection, content_type='application/json')


def configure_plain_text_api(api):
    api.add_representation(
            ExceptionRepresentation, content_type='text/plain',
            _transform_func=restosaur_exception_dict_as_text,
            qvalue=0.1)


def api_factory(path=None, api_class=API, **kwargs):
    api = api_class(path, **kwargs)
    return api


def json_api_factory(path=None, api_class=API, **kwargs):
    api = api_factory(path=path, api_class=api_class, **kwargs)
    return api
