from six import iteritems

from ...logger import logger

from ..error import Error
from ...user_warnings import UserWarnings

from ..namespaces.python_object_namespace import PythonObjectNamespace


class Set(object):

    def __init__(self, arguments, factory):
        self._paths = list()

        for key, value in iteritems(arguments['paths']):
            try:
                dest_path = factory.get_path(key)
                source_path = factory.get_path(value)
            except Exception as exc:
                message = "Failed to load dest:source path pair"
                logger.exception(message)
                UserWarnings.send_warning(Error(exc=exc, message=message))
                continue


            self._paths.append((dest_path, source_path))

    def execute(self, namespace):
        for dest_path, source_path in self._paths:
            try:
                value = source_path.read_from(namespace)
                if isinstance(value, PythonObjectNamespace) and \
                        value.dump_config == PythonObjectNamespace.ObjectDumpConfig.default_limits(value.obj):
                    value.dump_config = PythonObjectNamespace.ObjectDumpConfig.tailor_limits(value.obj)

                dest_path.write_to(namespace, value)
            except Exception as exc:
                message = "Failed to execute dest:source path pair"
                logger.exception(message)
                UserWarnings.send_warning(Error(exc=exc, message=message))
                continue
