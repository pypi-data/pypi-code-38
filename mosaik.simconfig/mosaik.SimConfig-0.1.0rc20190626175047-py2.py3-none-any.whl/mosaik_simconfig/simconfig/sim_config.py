import importlib
import os
import sys

from mosaik_api import Simulator

from collections.abc import Mapping


class SimConfig(Mapping):
    """
    Mosaik simulation configuration extending a read-only dictionary interface.
    """
    def __init__(self, *args, **kwargs):
        self._configuration = dict(*args, **kwargs)

    def __getitem__(self, key):
        return self._configuration[key]

    def __iter__(self):
        return iter(self._configuration)

    def __len__(self):
        return len(self._configuration)

    def add_in_process(self, *,
                       simulator):
        """
        Add a mosaik simulator written in Python
        to be executed in the main process.

        :rtype: None
        """
        simulator_name = simulator.__name__
        simulator_module = simulator.__module__

        self._configuration.update(
            {
                simulator_name:
                    {'python': simulator_module + ':' + simulator_name}
            }
        )

    def add_in_subprocess_java(self, *,
                               java: str = 'java', simulator_jar: str,
                               simulator_class: str) -> None:
        """
        Add a mosaik simulator written in Java
        to be executed in a subprocess.

        :rtype: None
        """
        command = ' '.join(
            [java, '-cp', simulator_jar, simulator_class, '%(addr)s'])
        simulator_name = simulator_jar[:-len('.jar')]

        self.add_in_subprocess(
            command=command,
            simulator_name=simulator_name,
        )

    def add_in_subprocess_python(self, *,
                                 python: str = sys.executable,
                                 simulator: Simulator, env: str = None,
                                 cwd: str = '.') -> None:
        """
        Add a mosaik simulator written in Python
        to be executed in a subprocess.

        :rtype: None
        """
        command = python + ' ' + \
            importlib.import_module(simulator.__module__).__file__ + ' ' + \
            '%(addr)s'
        simulator_name = simulator.__name__

        self.add_in_subprocess(
            command=command,
            cwd=cwd,
            env=env,
            simulator_name=simulator_name,
        )

    def add_in_subprocess_executable_standalone(self, *,
                                                cwd='.', env=None,
                                                simulator_exe):
        """
        Add a mosaik simulator
        compiled to an executable
        to be executed in a subprocess.

        This should work for C# console applications under Windows.
        Make sure PATH contains dotnet.exe, though.

        :rtype: None
        """
        command = './' + simulator_exe + ' ' + '%(addr)s'
        simulator_name = os.path.splitext(os.path.basename(simulator_exe))[0]

        self.add_in_subprocess(
            command=command,
            cwd=cwd,
            env=env,
            simulator_name=simulator_name,
        )

    def add_in_subprocess_c_sharp_on_runtime(self, *,
                                             cwd='.', env=None,
                                             runtime='mono', simulator_exe):
        """
        Add a mosaik simulator
        written in C# compiled as a .Net Core console application
        to be executed in a subprocess
        by a runtime.

        :rtype: None
        """
        command = runtime + ' ' + simulator_exe + ' ' + '%(addr)s'
        simulator_name = os.path.basename(simulator_exe)

        self.add_in_subprocess(
            command=command,
            cwd=cwd,
            env=env,
            simulator_name=simulator_name,
        )

    def add_in_subprocess(self, *,
                          command: str, cwd: str = '.',
                          env: str = None, simulator_name: str) -> None:
        """
        Add a mosaik simulator written in any programming language
        to be executed in a subprocess.

        :rtype: None
        """

        # An mutable object should not be a parameter.
        # So create an empty dictionary here in private.
        env = env if env is not None else {}

        self._configuration.update(
            {
                simulator_name: {
                    'cmd': command,
                    'cwd': cwd,
                    'env': env,
                }
            }
        )

    def add_service(self, *,
                    host: str = 'localhost', port: str, name: str) -> None:
        """
        Add a mosaik simulator listening at the given address
        for mosaik to connect to it.

        :rtype: None
        """
        connect = host + ':' + port

        self._configuration.update(
            {
                name: {
                    'connect': connect,
                }
            }
        )
