from ievv_opensource.utils.ievvbuildstatic import pluginbase
from ievv_opensource.utils.logmixin import Logger
from ievv_opensource.utils.shellcommandmixin import ShellCommandError
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin


class Plugin(pluginbase.Plugin, ShellCommandMixin):
    """
    Run a script from package.json (I.E.: ``npm run <something>``.

    Examples:

        Lets say you have the following in your package.json::

            {
              "scripts": {
                "myscript": "echo 'hello'"
              }
            }

        You can then make this script run with::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.npmrun.Plugin(script='myscript'),
                    ]
                )
            )
    """
    name = 'npmrun'

    def __init__(self, script, script_args=None, **kwargs):
        """

        Args:
            script (str): The name of the key for the script in the ``scripts``
                object in ``package.json``.
            script_args (list): Arguments for the script as a list of strings.
            **kwargs: Kwargs for :class:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin`.
        """
        self.script = script
        self.script_args = script_args
        super(Plugin, self).__init__(**kwargs)

    def run(self):
        name = '"{script}" package.json script'.format(script=self.script)
        self.get_logger().command_start('Running the {name} for {appname}'.format(
            name=name,
            appname=self.app.appname))
        try:
            self.app.get_installer('npm').run_packagejson_script(
                script=self.script,
                args=self.script_args or [])
        except ShellCommandError:
            self.get_logger().command_error('{name} FAILED!'.format(name=name))
            raise SystemExit()
        else:
            self.get_logger().command_success('{name} succeeded :)'.format(name=name))
