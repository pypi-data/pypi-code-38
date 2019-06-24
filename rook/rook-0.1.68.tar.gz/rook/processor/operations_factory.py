from ..factory import Factory

from . import operations


class OperationsFactory(Factory):

    def __init__(self, extended_operations_factories):
        super(OperationsFactory, self).__init__()

        self.register_methods(operations.__all__)
        self.import_methods(extended_operations_factories)

    def get_operation(self, configuration, factory):
        return self.get_object(configuration['name'], configuration, factory)
