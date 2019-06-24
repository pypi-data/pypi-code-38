import sys
import time

from django.conf import settings

from ievv_opensource.utils.ievvdevrun.runnables import base


class RunnableThread(base.ShellCommandRunnableThread):
    """
    Django-DBdev run database runnable thread.

    Examples:

        You can just add it to your Django development settings with::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.dbdev_runserver.RunnableThread()
                )
            }

    """

    def get_logger_name(self):
        return 'Django-dbdev database server: {!r}'.format(
            settings.DATABASES['default']
        )

    def get_command_config(self):
        return {
            'executable': sys.executable,
            'args': ['manage.py', 'dbdev_startserver']
        }

    def dbdev_stopserver(self):
        self.run_shell_command(sys.executable,
                               args=['manage.py', 'dbdev_stopserver'])

    def start(self):
        super(RunnableThread, self).start()
        time.sleep(4)  # Block to give the server time to start.

    def run(self):
        self.dbdev_stopserver()
        super(RunnableThread, self).run()

    def stop(self):
        super(RunnableThread, self).stop()
        self.dbdev_stopserver()
