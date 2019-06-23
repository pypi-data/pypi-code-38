"""Generic interactive shell with online help and auto completion support"""
import os
from friendlyshell.base_shell import BaseShell
from friendlyshell.shell_help_mixin import ShellHelpMixin
from friendlyshell.command_complete_mixin import \
    CommandCompleteMixin, auto_complete_manager
from friendlyshell.basic_logger_mixin import BasicLoggerMixin


class BasicShell(
        BasicLoggerMixin, BaseShell, ShellHelpMixin, CommandCompleteMixin):
    """Friendly Shell with basic online help and command auto-completion"""
    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super(BasicShell, self).__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        """Entry point method that launches our interactive shell.

        Input will be processed from the console to execute commands, until
        termination of the shell is invoked by the user via 'exit' or some
        other failure event.
        """
        # The history file for this shell should be named after the
        # derived class, so that each Friendly Shell implementation has
        # it's own unique history associated with it
        history_filename = os.path.join(self._config_folder,
                                        self.__class__.__name__ + ".hist")

        # Configure our auto-completion callback
        with auto_complete_manager(self.complete_key, self._complete_callback,
                                   history_filename):
            super(BasicShell, self).run(*args, **kwargs)


if __name__ == "__main__":
    pass
