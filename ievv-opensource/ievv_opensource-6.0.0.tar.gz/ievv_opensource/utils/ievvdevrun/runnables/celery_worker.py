import sys

from ievv_opensource.utils.ievvdevrun.runnables import base


class RunnableThread(base.ShellCommandRunnableThread):
    """
    Celery worker runnable thread.

    Examples:

        You can just add it to your Django development settings with::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.celery_worker.RunnableThread(
                        app='myproject')
                )
            }

        And you can make it not restart on crash with::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.celery_worker.RunnableThread(
                        app='myproject',
                        autorestart_on_crash=False)
                )
            }

    """
    default_autorestart_on_crash = True

    def __init__(self, app, loglevel='debug'):
        """
        Args:
            app: The Celery app to start - the python path to the module where you
                import your celery app in ``__init__.py``.
            loglevel: The Celery loglevel (``-l`` command line argument). Defaults to ``"debug"``.
        """
        self.app = app
        self.loglevel = loglevel
        super(RunnableThread, self).__init__()

    def get_logger_name(self):
        return 'Celery worker'

    def get_command_config(self):
        return {
            'executable': 'celery',
            'args': ['-A', self.app, 'worker', '-l', self.loglevel]
        }
