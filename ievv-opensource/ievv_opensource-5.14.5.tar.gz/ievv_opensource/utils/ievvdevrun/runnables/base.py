import threading
import time

import psutil

from ievv_opensource.utils import logmixin
from ievv_opensource.utils import shellcommandmixin


class AbstractRunnableThread(threading.Thread, logmixin.LogMixin):
    """
    Abstract class for a thread that runs something for the ``ievvdevrun`` framework.

    You have to override the ``run()``-method (refer to the docs for ``threading.Thread.run``),
    and the :meth:`~AbstractRunnableThread.stop` method.
    """
    def __init__(self, name=None):
        """
        Parameters:
            name: An optional name for the logger.
                See :meth:`~AbstractRunnableThread.get_logger_name`.
        """
        self.logger_name = name
        super(AbstractRunnableThread, self).__init__()

    def log_startup(self):
        """
        Called automatically on startup with ``"Starting <name>"`` message.
        """
        self.get_logger().info('Starting {}'.format(self.get_logger_name()))

    def log_successful_stop(self, message=''):
        """
        Call this in :meth:`.stop` to show a message after successfully stopping
        the runnable.

        Parameters:
            message: Optional extra message to show.
        """
        self.get_logger().info('{} stopped ! {}'.format(
            self.get_logger_name(), message))

    def start(self):
        self.log_startup()
        return super(AbstractRunnableThread, self).start()

    def get_logger_name(self):
        """
        Get the logger name. Defaults to the ``name``-parameter and falls back
        on the module name of the class.
        """
        return self.logger_name or self.__class__.__module__

    def stop(self):
        """
        Must stop the code running in the thread (the code in the run method).
        """
        raise NotImplementedError()


class ShellCommandRunnableThread(AbstractRunnableThread,
                                 shellcommandmixin.ShellCommandMixin):
    """
    Makes it very easy to implement :class:`.AbstractRunnableThread`
    for system/shell commands.

    Examples:

        Implement Django runserver::

            class DjangoRunserverRunnableThread(base.ShellCommandRunnableThread):
                def get_logger_name(self):
                    return 'Django development server'

                def get_command_config(self):
                    return {
                        # We use sys.executable instead of "python" to ensure we run the same python executable
                        # as we are using to start the process.
                        'executable': sys.executable,
                        'args': ['manage.py', 'runserver']
                    }

        As you can see, we just need specify the name and the command we want
        to run. You can even do this without creating a class by
        sending the command config as a parameter to this class
        in your django settings::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.base.ShellCommandRunnableThread(
                        name='Django development server',
                        command_config={
                            'executable': sys.executable,
                            'args': ['manage.py', 'runserver']
                        }
                    ),
                )
            }


        Making the command automatically restart when it crashes::

            class DjangoRunserverRunnableThread(base.ShellCommandRunnableThread):
                default_autorestart_on_crash = True
                # ... same code as the example above ...

        You can also autorestart by sending ``autorestart_on_crash=True``
        as a parameter for the class.
    """

    #: The default value for the ``autorestart_on_crash`` parameter.
    #: You can override this in subclasses if it is more natural
    #: to automatically restart on crash by default.
    default_autorestart_on_crash = False

    def __init__(self, name=None, command_config=None, autorestart_on_crash=None):
        """
        Parameters:
            name: Optional name for the runnable. Defaults to the module name.
            command_config: Same format as the return value from
                :meth:`.get_command_config`.
            autorestart_on_crash: Set this to ``True`` if you want to
                automatically restart the process if it crashes.
        """
        self.command_config = command_config
        if autorestart_on_crash is None:
            autorestart_on_crash = self.default_autorestart_on_crash
        self.autorestart_on_crash = autorestart_on_crash
        super(ShellCommandRunnableThread, self).__init__(name=name)

    def _restartloop(self):
        while True:
            if self.is_running:
                if self.command.process.is_alive():
                    try:
                        process = psutil.Process(self.command.pid)
                    except psutil.NoSuchProcess:
                        pass
                    else:
                        self.detected_process_ids.add(self.command.pid)
                        for childprocess in process.children():
                            self.detected_process_ids.add(childprocess.pid)
                else:
                    self.get_logger().warning('Restarting "{}" because of crash.'.format(
                        self.get_logger_name()))
                    self._start_command(restart=True)
            else:
                return

            # Check if alive every 5 second, but check if we have been stopped
            # every 200ms.
            for x in range(25):
                time.sleep(0.2)
                if not self.is_running:
                    break

    def _start_command(self, restart=False):
        if restart:
            self.stop()
        self.is_running = True
        self.detected_process_ids = set()
        commandconfig = self.get_command_config()
        kwargs = commandconfig.get('kwargs', {}).copy()
        kwargs.update({'_bg': True})
        self.command = self.run_shell_command(commandconfig['executable'],
                                              args=commandconfig.get('args', []),
                                              kwargs=kwargs)

    def get_command_config(self):
        """
        Get the config for the shell/system command as a dict with the
        following keys:

        - ``executable``: The name of the executable (E.g.: ``python``, ``sqlite``, ...).
        - ``args``: Arguments for the executable as a list.
        - ``kwargs``: Keyword arguments for the executable as a dict. ``my_option: "myvalue"``
            is automatically translated to ``--my-option="myvalue"``.
        """
        if self.command_config:
            return self.command_config
        else:
            raise NotImplementedError('You must override get_command_config() or send '
                                      'command_config to __init__().')

    def run(self):
        self._start_command()
        if self.autorestart_on_crash:
            self._restartloop()

    def stop(self):
        self.is_running = False
        process_ids = set(self.terminate_process(self.command.pid))
        for process_id in self.detected_process_ids:
            process_ids.update(set(self.terminate_process(process_id)))
        self.log_successful_stop(
            '[killed pids: {}]'.format(', '.join(map(str, process_ids))))
