import os

from ievv_opensource.utils.logmixin import LogMixin
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin


class AbstractDocBuilder(LogMixin, ShellCommandMixin):
    """
    Base class for documentation builders.

    Each installer defines most of their own API, the only thing they
    have in common is a reference to their
    :class:`ievv_opensource.utils.ievvbuildstatic.config.App`,
    a :obj:`~.AbstractDocBuilder.name` and the methods
    defined in :class:`ievv_opensource.utils.logmixin.LogMixin`
    and :class:`ievv_opensource.utils.ievvbuildstatic.shellcommand.ShellCommandMixin`.

    An app runs all the doc builders in order. The first doc builder
    where :meth:`~.AbstractDocBuilder.is_available` returns ``True``
    is used for the app.
    """

    #: The name of the docbuilder.
    name = None

    def __init__(self, app):
        """
        Parameters:
            app: The :class:`ievv_opensource.utils.ievvbuildstatic.config.App` where
                this docbuilder object was instantiated.
        """
        self.app = app

    def get_logger_name(self):
        return '{}.{}'.format(self.app.get_logger_name(), self.name)

    def get_loglevel(self):
        return self.app.apps.loglevel

    def is_available(self):
        """
        Is this docbuilder available in the app?
        """
        return False

    def build_docs(self, output_directory):
        raise NotImplementedError()
