from .. import urltemplate


class ResourceAlreadyRegistered(Exception):
    pass


def autogenerate_resource_name(resource):
    path = urltemplate.remove_parameters(resource.path)

    try:
        name = list(filter(None, path.split('/')))[-1]
    except IndexError:
        name = '/'

    return name


def always_true(context):
    return True


class ApiRoot(object):
    def __init__(self, root_resource=None):
        """
        Creates instance of ApiRoot registry.

        If `root_resource` is provided, the ApiRoot`s view will be registered
        as a root_resource`s service for HTTP GET method.
        """

        self.resources = {}

        if root_resource:
            root_resource.get()(self.as_view())
            root_resource.add_representation(
                    model=type(self), content_type='application/json',
                    _transform_func=type(self).as_dict)

    def register(self, resource, name=None, condition=None):
        name = name or autogenerate_resource_name(resource)

        if name in self.resources:
            raise ResourceAlreadyRegistered(name)
        condition = condition or always_true
        self.resources[name] = {'resource': resource, 'condition': condition}

    def expose(self, name, condition=None):
        def wrap(resource):
            self.register(resource, name, condition=condition)
            return resource
        return wrap

    def as_dict(self, ctx):
        data = {}

        for name, meta in self.resources.items():
            if meta['condition'](ctx):
                data[name] = meta['resource'].uri(ctx)

        return data

    def as_view(self):
        def get_api_root(ctx):
            return ctx.OK(self)
        return get_api_root
