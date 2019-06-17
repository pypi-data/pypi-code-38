from ..logger import logger

from .error import Error
from ..user_warnings import UserWarnings


class Processor(object):

    def __init__(self, script, factory):
        self._operations = []

        for operation in script:
            self._operations.append(factory.get_operation(operation))

    def process(self, namespace):

        for operation in self._operations:
            try:
                result = operation.execute(namespace)
            except Exception as exc:
                message = "Error in operation"
                logger.exception(message)
                UserWarnings.send_warning(Error(exc=exc, message=message))
                return

            if result is not None:
                return result
