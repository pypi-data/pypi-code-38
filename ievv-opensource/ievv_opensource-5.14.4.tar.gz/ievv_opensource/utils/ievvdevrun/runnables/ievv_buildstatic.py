import sys

from ievv_opensource.utils.ievvdevrun.runnables import base


class RunnableThread(base.ShellCommandRunnableThread):
    """
    ``ievv buildstatic --watch`` runnable thread.

    Examples:

        You can just add it to your Django development settings with::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.ievv_buildstatic.RunnableThread()
                )
            }

    """
    default_autorestart_on_crash = True

    def get_logger_name(self):
        return 'ievv buildstatic --watch'

    def get_command_config(self):
        return {
            'executable': sys.executable,
            'args': ['manage.py', 'ievvtasks_buildstatic', '--watch']
        }
