from six import iteritems

from ...logger import logger

from ..namespaces.python_object_namespace import PythonObjectNamespace
from ..namespaces.container_namespace import ContainerNamespace


class Exec(object):

    def __init__(self, arguments, factory):
        self._statements = arguments['statements']

    def execute(self, namespace):
        if isinstance(namespace, ContainerNamespace):
            exec_locals = namespace
        else:
            exec_locals = {}

        try:
            exec(self._statements, exec_locals)
        except Exception:
            logger.exception("exec threw an exception")
