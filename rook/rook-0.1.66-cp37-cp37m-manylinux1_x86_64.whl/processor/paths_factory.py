from ..factory import Factory

from .paths.arithmetic_path import ArithmeticPath


class PathsFactory(Factory):

    try:
        STRING_TYPES = (str, unicode)
    except NameError:
        STRING_TYPES = (str, )

    def __init__(self, extended_paths_factories):
        super(PathsFactory, self).__init__()

        self.register_method(ArithmeticPath)

        if extended_paths_factories:
            self.register_methods(extended_paths_factories)

    def get_path(self, configuration, factory):
        if isinstance(configuration, self.STRING_TYPES):
            return ArithmeticPath(configuration)
        else:
            return self.get_object(configuration['name'], configuration, factory)
