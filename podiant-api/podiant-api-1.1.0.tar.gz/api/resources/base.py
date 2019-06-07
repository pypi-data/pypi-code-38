from api.exceptions import ConfigurationError
from .links import ResourceLink


class ResourceBase(object):
    def __init__(self, **kwargs):
        """
        Initialises the reousrce with an arbitrary set of keyword arguments,
        later to be used when finding a specific object
        """

        self.kwargs = kwargs

    def get_form_class(self, fields=None):
        """
        Returns the form class used to interact with the resource. Only
        override this method if you need to use a factory to produce the form;
        othersie you can define the class via the `form_class` property.
        """

        if hasattr(self, 'form_class'):
            return self.form_class

        raise ConfigurationError(  # pragma: no cover
            'form_class not defined'
        )

    def get_form_kwargs(self, form_class):  # pragma: no cover
        """
        Returns the keyword arguments passed to a form class's init method.
        Override this method to add resource-form-specific kwargs.
        """

        return {}

    def get_form(self, *args, **kwargs):
        """
        Returns a form by getting the form class and instantiating it with the
        form kwargs (and applying any kwargs from this method). Override this
        method if you need to alter the form before it's used.
        """

        form_class = self.get_form_class()
        kw = self.get_form_kwargs(form_class)
        kw.update(kwargs)
        form = form_class(**kw)

        return form

    def pack(self, depth=0):  # pragma: no cover
        """
        Override this method to return a JSON-API representation of a
        resource object.
        """

        raise NotImplementedError('Method not implemented')

    def unpack(self, data):  # pragma: no cover
        """
        Override this method to return a dictionary converted from a JSON-API
        object.
        """

        raise NotImplementedError('Method not implemented')

    def link(self, *args, **kwargs):
        """
        Returns a `ResourceLink` object that can be later resolved and
        deserialised into a URL to an API URL.
        """

        return ResourceLink(*args, **kwargs)


class ResourceDetailBase(ResourceBase):
    def get_object(self):  # pragma: no cover
        """
        Override this method to return an object givne a set of criteria.
        """

        raise NotImplementedError('Method not implemented')


class ResourceListBase(ResourceBase):
    def get_objects(self):  # pragma: no cover
        """
        Override this method to return an object list givne a set of criteria.
        """

        raise NotImplementedError('Method not implemented')

    def get_initial(self):  # pragma: no cover
        """
        Returns the initial data used to populate a form. Override this
        method to add prepopulated data for a resource object.
        """

        return {}
