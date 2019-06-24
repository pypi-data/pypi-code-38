import logging
import six
import traceback
import time

from ..processor.namespaces.container_namespace import ContainerNamespace
from ..processor.namespaces.python_object_namespace import PythonObjectNamespace


class NamespaceSerializerHandler(logging.Handler):

    output = None

    try :
        STRING_TYPES = (str, unicode)
    except NameError:
        STRING_TYPES = (str, )

    def __init__(self):
        super(NamespaceSerializerHandler, self).__init__()

    def emit(self, record):
        if not self.output:
            return

        try:
            arguments = {}

            try:
                formatted_message = record.getMessage()
            except:
                formatted_message = ""

            # If message is a pure string, record it, else add to arguments dictionary
            if isinstance(record.msg, self.STRING_TYPES):
                raw_message = record.msg
            else:
                raw_message = ""
                arguments['msg'] = PythonObjectNamespace(record.msg)

            # Add exception to arguments dictionary
            if record.exc_info:
                arguments['exc_type'] = PythonObjectNamespace(record.exc_info[0])
                arguments['exc_instance'] = PythonObjectNamespace(record.exc_info[1])
                arguments['traceback'] = PythonObjectNamespace(record.exc_info[2])

            # Add additional arguments to arguments dictionary
            if record.args:
                arguments['args'] = PythonObjectNamespace(record.args)

            # Send record information to output
            self.output.send_log_message(record.levelno, record.created or time.time(), record.pathname, record.lineno, formatted_message, formatted_message, arguments)
        except Exception:
            six.print_("Unexpected error when writing to log")
            traceback.print_exc()
