import inspect
import six
from collections import defaultdict

from .loading import load_resource


DEFAULT_LINK_NAME = '__default__'


def model_class(instance_or_class):
    return type(instance_or_class) if not inspect.isclass(
            instance_or_class) else instance_or_class


class ModelAlreadyLinked(Exception):
    pass


class ModelNotLinked(Exception):
    pass


class MissingRequiredParameters(Exception):
    pass


class ModelLinksRegistry(object):
    def __init__(self):
        self._links = defaultdict(dict)

    def link(self, model, resource, name=None):
        """
        Create named link between a model and resource
        """

        name = name or DEFAULT_LINK_NAME
        cls = model_class(model)
        if name in self._links[cls]:
            raise ModelAlreadyLinked(
                    '%s is already linked to %s as "%s"' % (
                        cls, resource, name))
        self._links[cls][name] = resource

    def unlink(self, model, name=None):
        """
        Remove named link.
        If name is not provided, all model links will be removed.
        """

        cls = model_class(model)
        links = self._links[cls]

        if not links:
            raise ModelNotLinked(cls)

        if not name:
            self._links[cls] = {}
        else:
            if name not in links:
                raise ModelNotLinked(
                    '%s has no "%s" link registered' % (cls, name))
            del links[name]

    def instance_links(self, instance):
        """
        Return list of registered links for a model instance
        """

        return self._links[type(instance)]

    def class_links(self, cls):
        """
        Return list of registered links for a model class
        """

        return self._links[cls]

    def linked_resource(self, model, name=None):
        """
        Return resource for model class named link
        """
        name = name or DEFAULT_LINK_NAME

        if not inspect.isclass(model):
            model = type(model)

        try:
            resource = self._links[model][name]
        except KeyError:
            raise ModelNotLinked(
                    '%s has no "%s" link registered' % (model, name))

        if isinstance(resource, six.string_types):
            resource = load_resource(resource)
            self._links[model][name] = resource

        return resource

    def url(
            self, context, instance_or_class, name=None, parameters=None,
            query=None):
        if inspect.isclass(instance_or_class):
            return self.url_for_class(
                    context, instance_or_class, name=name, query=query,
                    parameters=parameters)
        else:
            return self.url_for_instance(
                    context, instance_or_class, name=name, query=query)

    def url_for_instance(
            self, context, instance, name=None, query=None):
        """
        Generate URL for a model instance based on registered links.
        Path parameters will be read from the model instance.
        Optional query args may be provided.
        """

        name = name or DEFAULT_LINK_NAME
        resource = self.linked_resource(type(instance), name=name)

        if not resource._required_parameters:
            return resource.uri(self, query=query)

        params = {}

        for parameter in resource._required_parameters:
            try:
                params[parameter] = getattr(instance, parameter)
            except AttributeError:
                try:
                    params[parameter] = instance[parameter]
                except (KeyError, TypeError, ValueError):
                    raise ValueError(
                        'Can\'t construct URL parameter "%s" from `%s`' % (
                            parameter, instance))

        return resource.uri(context, params=params, query=query)

    def url_for_class(
            self, context, cls, name=None, parameters=None, query=None):
        """
        Generate URL for a model class based on registered links.
        Path parameters should be provided.
        Optional query args may be also provided.
        """

        name = name or DEFAULT_LINK_NAME
        resource = self.linked_resource(cls, name=name)
        parameters = parameters or {}

        missing_parameters = []

        for parameter in resource._required_parameters:
            if parameter not in parameters:
                missing_parameters.append(parameter)

        if missing_parameters:
            raise MissingRequiredParameters(missing_parameters)

        return resource.uri(context, params=parameters, query=query)
