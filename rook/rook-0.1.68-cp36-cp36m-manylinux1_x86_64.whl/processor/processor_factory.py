
from .operations_factory import OperationsFactory
from .paths_factory import PathsFactory
from .processor import Processor


class ProcessorFactory(object):

    def __init__(self, extended_operations_factories, extended_path_factories):
        self.operations_factory = OperationsFactory(extended_operations_factories)
        self.paths_factory = PathsFactory(extended_path_factories)

    def register_operation(self, operation):
        self.operations_factory.register_method(operation)

    def get_operation(self, configuration):
        return self.operations_factory.get_operation(configuration, self)

    def get_path(self, configuration):
        return self.paths_factory.get_path(configuration, self)

    def get_processor(self, configuration):
        return Processor(configuration, self)
