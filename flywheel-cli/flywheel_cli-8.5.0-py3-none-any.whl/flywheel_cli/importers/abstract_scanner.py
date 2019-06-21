from abc import ABC, abstractmethod
import logging


log = logging.getLogger(__name__)


class AbstractScanner(ABC):
    """Abstract base class for Scanners"""
    def __init__(self, config):
        self.config = config
        self.messages = []

    @abstractmethod
    def discover(self, walker, context, container_factory, path_prefix=None, audit_log=None):
        """Performs discovery of containers to create and files to upload in the given folder.

        Arguments:
            walker (AbstractWalker): The filesystem to query
            context (dict): The initial context
            container_factory (obj): The ContainerFactory instance
            path_prefix (str): The optional prefix for filenames
            audit_log (AuditLog): The optional audit_log instance
        """

    # def add_log(self, src_path, container, file_name, failed=False, message=None):
    def report_file_error(self, audit_log, path, exc=False, msg=None):
        """Report that a file error has occurred, along with the given message.

        Arguments:
            audit_log (AuditLog): The audit log instance
            path (str): The full path to the file that could not be read
            message (str): The error message
            exc (Exception): The exception that occurred, if applicable
        """
        log_msg = 'Error reading file %s: %s' % (path, msg or exc)

        # Report to audit_log
        if audit_log is not None:
            audit_log.add_log(path, None, None, failed=True, message=log_msg)

        # Add it to the debug log
        log.debug('%s', log_msg, exc_info=exc)

        # Add it as a message
        # TODO: Configurable warnings-as-errors?
        self.messages.append(('warn', log_msg))
