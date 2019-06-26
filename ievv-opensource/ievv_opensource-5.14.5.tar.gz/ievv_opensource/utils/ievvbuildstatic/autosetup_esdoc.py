import json
import os

from ievv_opensource.utils.ievvbuildstatic import pluginbase
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin


class Plugin(pluginbase.Plugin, ShellCommandMixin):
    """
    Autosetup esdoc config and npm script.

    The plugin creates the esdoc.json config file automatically.
    It also creates a directory named ``esdoc`` and a file
    named ``index.md`` within that directory. That file is
    the frontpage of your docs, and you should edit it and provide
    some information about the app/library.

    If you want to add a manual "page" to your docs, you do that
    by adding files and/or directories to the ``esdoc/manual/`` directory
    (relative to the source directory - the directory with package.json).
    Esdoc has a specific set of manual sections that you can add:

    - asset
    - overview
    - installation
    - usage
    - tutorial
    - configuration
    - example
    - faq
    - changelog

    This plugin automatically adds these to the ``esdoc.json`` with the following
    rules:

    - Does ``esdoc/manual/<section>.md`` exist? Add that as the first entry in
      the ``manual.<section>`` list.
    - Does ``esdoc/manual/<section>/`` exist? Add all .md files in that directory
      to the ``manual.<section>`` list in sorted order.

    Examples:

        It is really simple to use::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.autosetup_esdoc.Plugin(),
                    ]
                )
            )

        Lets add a tutorial! First create ``esdoc/manual/tutorial.md`` and run ievv buildstatic.
        That file should end up in ``esdoc.json`` and if you build the docs
        you should get a "manual" link at the top of the manual. If your tutorial grows,
        simply create the ``esdoc/manual/tutorial/`` directory and add markdown files to
        it. The files are sorted by filename and the output in the docs is still
        a single file. The ``esdoc/manual/tutorial.md`` file will still end up first if
        it is present. You can choose if you want to use the ``esdoc/manual/tutorial.md``,
        the ``esdoc/manual/tutorial/`` directory or both. The tutorial example works
        for all the manual sections documented above.
    """
    name = 'autosetup_esdoc'

    def __init__(self, title=None, **kwargs):
        """

        Args:
            title (str): The title of the docs. Falls back to the app name
                if not specified.
            **kwargs: Kwargs for :class:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin`.
        """
        super(Plugin, self).__init__(**kwargs)
        self.title = title

    def install(self):
        """
        Installs the ``esdoc`` and ``esdoc-importpath-plugin``
        npm packages as dev dependencies.
        """
        self.app.get_installer('npm').queue_install(
            package='esdoc',
            installtype='dev'
        )
        self.app.get_installer('npm').queue_install(
            package='esdoc-importpath-plugin',
            installtype='dev'
        )

    def get_esdoc_config_path(self):
        return self.app.get_source_path('esdoc.json')

    def get_manual_path(self, *path):
        return self.app.get_source_path('esdoc', 'manual', *path)

    def get_esdoc_index_path(self):
        return self.app.get_source_path('esdoc', 'index.md')

    def esdoc_index_exists(self):
        return os.path.exists(self.get_esdoc_index_path())

    def get_default_esdoc_index_content(self):
        return '**TODO:** edit this text in ``{esdoc_index_path}``.'.format(
            esdoc_index_path=self.app.make_source_relative_path(
                self.get_esdoc_index_path())
        )

    def create_default_esdoc_index(self):
        filepath = self.get_esdoc_index_path()
        directorypath = os.path.dirname(filepath)
        if not os.path.exists(directorypath):
            os.makedirs(directorypath)
        open(filepath, 'w').write(
            self.get_default_esdoc_index_content())

    def _add_manual_dict_files_for_section(self, section):
        directory_path = self.get_manual_path(section)
        file_path = self.get_manual_path('{}.md'.format(section))
        file_list = []
        if os.path.exists(file_path):
            file_list.append(self.app.make_source_relative_path(file_path))
        if os.path.exists(directory_path):
            for filename in sorted(os.listdir(directory_path)):
                if filename.endswith('.md'):
                    path = self.app.make_source_relative_path(
                        os.path.join(directory_path, filename))
                    file_list.append(path)
        return file_list

    def make_manual_dict(self):
        manual_dict = {}
        for section in ('asset', 'overview', 'installation', 'usage',
                        'tutorial', 'configuration', 'example', 'faq',
                        'changelog'):
            file_list = self._add_manual_dict_files_for_section(section=section)
            if file_list:
                manual_dict[section] = file_list
        return manual_dict

    def make_plugins_list(self):
        return [
            {
                "name": "esdoc-importpath-plugin",
                "option": {
                    "replaces": [
                        {
                            "from": "^javascript/",
                            "to": ""
                        },
                        {
                            "from": "^{appname}/".format(appname=self.app.appname),
                            "to": ""
                        }
                    ]
                }
            }
        ]

    def make_esdoc_config_dict(self):
        config_dict = {
            "title": self.title or self.app.appname,
            "source": self.app.make_source_relative_path("scripts", "javascript"),
            "destination": self.app.make_source_relative_path("built_docs"),
            "includes": ["\\.(js|es6|jsx)$"],
            "excludes": [
                "__tests__.+$",
                "__mocks__.+$"
            ],
            "index": self.app.make_source_relative_path(self.get_esdoc_index_path()),
        }
        plugins_list = self.make_plugins_list()
        if plugins_list:
            config_dict['plugins'] = plugins_list
        manual_dict = self.make_manual_dict()
        if manual_dict:
            config_dict['manual'] = manual_dict
        return config_dict

    def create_esdoc_config(self):
        open(self.get_esdoc_config_path(), 'w').write(
            json.dumps(
                self.make_esdoc_config_dict(),
                indent=2,
                sort_keys=True
            ))

    def run(self):
        self.get_logger().command_start('Autosetup esdoc for {appname}'.format(
            appname=self.app.appname))
        if not self.esdoc_index_exists():
            self.create_default_esdoc_index()
        self.create_esdoc_config()
        self.app.get_installer('npm').add_npm_script(
            'build-docs', 'esdoc -c {configpath}'.format(
                configpath=self.app.make_source_relative_path(self.get_esdoc_config_path())))
        self.get_logger().command_success('Autoset esdoc config succeeded :)')
