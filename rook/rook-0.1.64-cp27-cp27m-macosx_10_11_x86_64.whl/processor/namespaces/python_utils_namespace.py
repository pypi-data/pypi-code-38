
import six
import sys
import threading
import os

from .namespace import Namespace

from .python_object_namespace import PythonObjectNamespace
from .container_namespace import ContainerNamespace
from .collection_namespace import ListNamespace
from .frame_namespace import FrameNamespace

from .stack_namespace import StackNamespace

from ...logger import logger


class PythonUtilsNamespace(Namespace):

    def __init__(self):
        super(PythonUtilsNamespace, self).__init__(self.METHODS)

    def read_attribute(self, name):
        raise NotImplementedError()

    def exception(self, args):
        return PythonObjectNamespace(sys.exc_info()[1])

    def exception_string(self, args):
        if six.PY2:
            return PythonObjectNamespace(unicode(sys.exc_info()[1]))
        else:
            return PythonObjectNamespace(str(sys.exc_info()[1]))

    def exception_type(self, args):
        return PythonObjectNamespace(sys.exc_info()[0])

    def module(self, args):
        return PythonObjectNamespace(sys.modules[args])

    def thread_id(self, args):
        return PythonObjectNamespace(threading.currentThread().ident)

    def thread_name(self, args):
        return PythonObjectNamespace(threading.currentThread().name)

    def threads(self, args):
        return PythonObjectNamespace(threading.enumerate())

    def thread_tracebacks(self, args):
        threads = threading.enumerate()
        frames = sys._current_frames()

        result = []
        for thread in threads:
            try:
                traceback = StackNamespace(FrameNamespace(frames[thread.ident])).traceback(None)
            except KeyError:
                traceback = PythonObjectNamespace(None)

            result.append(ContainerNamespace({
                'id': PythonObjectNamespace(thread.ident),
                'name': PythonObjectNamespace(thread.name),
                'daemon': PythonObjectNamespace(thread.daemon),
                'traceback': traceback,
            }))

        return ListNamespace(result)

    def env(self, args):
        try:
            value = os.environ[args]
        except KeyError:
            logger.exception("Failed to get env variable")
            value = None

        return PythonObjectNamespace(value)

    METHODS = (exception, exception_string, exception_type, module, thread_id, thread_name, threads, thread_tracebacks, env)
