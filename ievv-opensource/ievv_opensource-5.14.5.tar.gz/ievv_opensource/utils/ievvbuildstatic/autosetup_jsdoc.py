import json

from ievv_opensource.utils.ievvbuildstatic import pluginbase
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin


class Plugin(pluginbase.Plugin, ShellCommandMixin):
    """
    Autosetup jsdoc config and npm script.

    Examples:

        It is really simple to use::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.autosetup_jsdoc.Plugin(),
                    ]
                )
            )

        If you need to adjust the config, simply setup
        your own ``build-docs`` script in package.json instead
        of using this plugin.
    """
    name = 'autosetup_jsdoc'

    def install(self):
        self.app.get_installer('npm').queue_install(
            package='jsdoc',
            installtype='dev'
        )

    def get_jsdoc_config_filename(self):
        return 'jsdoc.config.json'

    def get_jsdoc_config_path(self):
        return self.app.get_source_path(self.get_jsdoc_config_filename())

    def make_jsdoc_config_dict(self):
        return {
            "opts": {
                "encoding": "utf8",
                "destination": "./built_docs/",
                "recurse": True
            },
            "source": {
                "includePattern": ".+\\.js(doc|x)?$",
                "excludePattern": "(^|\\/|\\\\)_",
                "include": [
                    "./scripts/javascript/"
                ]
            },
            "tags": {
                "allowUnknownTags": True,
                "dictionaries": ["jsdoc", "closure"]
            },
            "plugins": ["plugins/markdown"],
            "markdown": {
                "parser": "gfm"
            },
            "templates": {
                "cleverLinks": False,
                "monospaceLinks": False
            }
        }

    def create_jsdoc_config(self):
        open(self.get_jsdoc_config_path(), 'w').write(
            json.dumps(
                self.make_jsdoc_config_dict(),
                indent=2,
                sort_keys=True
            ))

    def run(self):
        self.get_logger().command_start('Autosetup jsdoc for {appname}'.format(
            appname=self.app.appname))
        self.create_jsdoc_config()
        self.app.get_installer('npm').add_npm_script(
            'build-docs', 'jsdoc -c {configpath}'.format(
                configpath=self.get_jsdoc_config_filename()))
        self.get_logger().command_success('Autoset jsdoc config succeeded :)')
