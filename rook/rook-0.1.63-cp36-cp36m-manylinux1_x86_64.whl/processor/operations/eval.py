from six import iteritems

from ...logger import logger

from ..namespaces.python_object_namespace import PythonObjectNamespace
from ..namespaces.container_namespace import ContainerNamespace


class Eval(object):

    def __init__(self, arguments, factory):
        self._paths = list()

        for key, value in iteritems(arguments['paths']):
            try:
                dest_path = factory.get_path(key)
                source_path = value
            except Exception:
                logger.exception("Failed to load dest:source path pair %s:%s", key, value)
                continue

            self._paths.append((dest_path, source_path))

    def execute(self, namespace):
        if isinstance(namespace, ContainerNamespace):
            eval_locals = namespace
        else:
            eval_locals = {}

        for dest_path, source_path in self._paths:
            try:
                value = eval(source_path, eval_locals)
                if isinstance(value, PythonObjectNamespace):
                    value.dump_config = PythonObjectNamespace.ObjectDumpConfig.tailor_limits(value.obj)

                dest_path.write_to(namespace, value)
            except Exception:
                logger.exception("Failed to execute dest:source path pair")
                continue
