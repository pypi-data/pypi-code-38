from ievv_opensource.utils.ievvbuildstatic import pluginbase
from ievv_opensource.utils.ievvbuildstatic.installers.npm import NpmInstaller
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin


class Plugin(pluginbase.Plugin, ShellCommandMixin):
    """
    NPM install plugin --- installs NPM packages.

    The packages are installed when ``ievv buildstatic`` starts up.

    Examples:

        Install uniq and momentjs packages::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.npminstall.Plugin(
                            packages={
                                'uniq': None,
                                'momentjs': None
                            }
                        ),
                    ]
                )
            )

        You can specify a version instead of ``None`` if you do not want
        to install the latest version.
    """
    name = 'npminstall'

    def __init__(self, packages, **kwargs):
        super(Plugin, self).__init__(**kwargs)
        self.packages = packages

    def install(self):
        for package, version in self.packages.items():
            self.app.get_installer('npm').queue_install(
                package, version=version)
