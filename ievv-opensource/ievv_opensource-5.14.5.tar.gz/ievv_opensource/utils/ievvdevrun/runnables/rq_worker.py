import sys
from ievv_opensource.utils.ievvdevrun.runnables import base


class RunnableThread(base.ShellCommandRunnableThread):
    """
    Django runserver runnable thread.
    Examples:
        You can just add it to your Django development settings with::
            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': devrun_rq_runnable.RunnableThreadList(
                    ievvdevrun.runnables.django_runserver.RunnableThread()
                )
            }
        And you can make it not restart on crash with::
            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': devrun_rq_runnable.RunnableThreadList(
                    ievvdevrun.runnables.django_runserver.RunnableThread(
                        autorestart_on_crash=False)
                )
            }
    """
    default_autorestart_on_crash = True

    def __init__(self, queuename='default'):
        """
        Args:
            queuename: The name of the queue
        """
        self.queuename = queuename
        super(RunnableThread, self).__init__()

    def get_logger_name(self):
        return 'RQ queue worker'

    def get_command_config(self):
        return {
            'executable': sys.executable,
            'args': ['manage.py', 'rqworker', self.queuename]
        }
