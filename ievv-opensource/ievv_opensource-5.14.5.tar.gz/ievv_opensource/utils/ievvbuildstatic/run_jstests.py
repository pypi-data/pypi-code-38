from ievv_opensource.utils.ievvbuildstatic import pluginbase
from ievv_opensource.utils.logmixin import Logger
from ievv_opensource.utils.shellcommandmixin import ShellCommandError
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin


class Plugin(pluginbase.Plugin, ShellCommandMixin):
    """
    Run javascript tests by running ``npm test`` if the
    ``package.json`` has a ``"test"`` entry in ``"scripts"``.

    Examples:

        Lets say you have the following in your package.json::

            {
              "scripts": {
                "test": "jest"
              }
            }

        You can then make ``jest`` run at startup (not on watch change)
        with::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.run_jstests.Plugin(),
                    ]
                )
            )

        If you have a NPM script named ``"test-debug"``, that will be run
        instead of ``"test"`` when loglevel is DEBUG. This means that
        if you add something like this to your package.json::

            {
              "scripts": {
                "test": "jest",
                "test-debug": "jest --debug"
              }
            }

        and run ``ievv buildstatic --debug``, ``jest --debug`` would
        be run instead of ``jest``.
    """
    name = 'run_jstests'
    default_group = 'jstest'

    def __init__(self, **kwargs):
        """

        Args:
            **kwargs: Kwargs for :class:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin`.
        """
        super(Plugin, self).__init__(**kwargs)

    def get_script_keys(self):
        scripts_dict = self.app.get_installer('npm').get_packagejson_dict().get('scripts', {})
        return scripts_dict.keys()

    def get_test_script_key(self):
        if self.get_loglevel() == Logger.DEBUG:
            script_keys = self.get_script_keys()
            if 'test-debug' in script_keys:
                return 'test-debug'
        return 'test'

    def log_shell_command_stderr(self, line):
        """
        Called by :meth:`.run_shell_command` each time the shell
        command outputs anything to stderr.
        """
        super(Plugin, self).log_shell_command_stdout(line=line)

    def has_tests(self):
        return self.get_test_script_key() in self.get_script_keys()

    def run(self):
        if self.has_tests():
            self.get_logger().command_start('Running tests for {appname}'.format(
                appname=self.app.appname))
            try:
                self.app.get_installer('npm').run_packagejson_script(
                    script=self.get_test_script_key(),
                    args=['--silent'])
            except ShellCommandError:
                self.get_logger().command_error('npm test FAILED!')
                raise SystemExit()
            else:
                self.get_logger().command_success('npm test succeeded :)')
