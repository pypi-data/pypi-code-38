import json

from ievv_opensource.utils.ievvbuildstatic import pluginbase
from ievv_opensource.utils.shellcommandmixin import ShellCommandError
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin


class Plugin(pluginbase.Plugin, ShellCommandMixin):
    """
    Bower install plugin --- installs bower packages.

    The packages are installed when ``ievv buildstatic`` starts up.
    The plugin creates a ``bower.json`` file, and runs ``bower install``
    using the created ``bower.json``-file.

    You will most likely want to add ``bower.json`` and ``bower_components``
    to your VCS ignore file.

    Examples:

        Install bootstrap 3.1.1 and angularjs 1.4.1::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.bowerinstall.Plugin(
                            packages={
                                'bootstrap': '~3.1.1',
                                'angular': '~1.4.1'
                            }
                        ),
                    ]
                )
            )
    """
    name = 'bowerinstall'

    def __init__(self, packages, **kwargs):
        super(Plugin, self).__init__(**kwargs)
        self.packages = packages

    def get_bowerjson_path(self):
        return self.app.get_source_path('bower.json')

    def create_bowerjson(self):
        packagedata = {
            'name': self.app.appname,
            'version': self.app.version,
            "private": True,
            "interactive": False,
            "analytics": False,
            "devDependencies": self.packages
        }
        open(self.get_bowerjson_path(), 'wb').write(
            json.dumps(packagedata, indent=2).encode('utf-8'))

    def get_bower_version(self):
        return None

    def install(self):
        self.app.get_installer('npm').queue_install(
            'bower', version=self.get_bower_version())

    def run(self):
        self.get_logger().command_start('Running bower install for {}'.format(
            self.app.get_source_path()))
        self.create_bowerjson()
        bower_executable = self.app.get_installer('npm').find_executable('bower')
        try:
            self.run_shell_command(bower_executable,
                                   args=['install'],
                                   _cwd=self.app.get_source_path())
        except ShellCommandError:
            self.get_logger().command_error('bower install FAILED!')
            raise SystemExit()
        else:
            self.get_logger().command_success('bower install succeeded :)')
