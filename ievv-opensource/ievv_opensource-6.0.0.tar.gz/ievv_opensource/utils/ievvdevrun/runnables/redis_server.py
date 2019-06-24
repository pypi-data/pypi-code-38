import sys

from ievv_opensource.utils.ievvdevrun.runnables import base


class RunnableThread(base.ShellCommandRunnableThread):
    """
    redis-server runnable thread.

    Examples:

        You can just add it to your Django development settings with::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.redis_server.RunnableThread()
                )
            }

        Or if you want Redis to run with your custom ``redis.conf`` file::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.redis_server.RunnableThread(config_path=/path/to/config/redis.conf)
                )
            }

        And you can make it not restart on crash with::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.redis_server.RunnableThread(
                        autorestart_on_crash=False)
                )
            }

    """
    default_autorestart_on_crash = True

    def __init__(self, port='6379', config_path=None):
        """
        Args:
            port: The port to run the Redis server on. Defaults to ``"6379"``.
            config_path: Path to the redis.conf file. Defaults to ``None``.
        """
        self.port = port
        self.config_path = config_path
        super(RunnableThread, self).__init__()

    def get_logger_name(self):
        return 'Redis server'

    def get_command_config(self):
        args = ['--port', str(self.port)]
        if self.config_path:
            args.insert(0, self.config_path)
        return {
            'executable': 'redis-server',
            'args': args
        }
