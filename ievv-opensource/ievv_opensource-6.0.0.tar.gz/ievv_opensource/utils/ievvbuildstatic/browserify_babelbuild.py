import json
import os

from . import browserify_jsbuild


class Plugin(browserify_jsbuild.Plugin):
    """
    Browserify javascript babel build plugin.

    Examples:

        Simple example::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.browserify_babelbuild.Plugin(
                            sourcefile='app.js',
                            destinationfile='app.js',
                        ),
                    ]
                )
            )

        Custom source folder example::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.browserify_babelbuild.Plugin(
                            sourcefolder=os.path.join('scripts', 'javascript', 'api'),
                            sourcefile='api.js',
                            destinationfile='api.js',
                        ),
                    ]
                )
            )

    """
    name = 'browserify_babelbuild'

    def __init__(self, echmascript_version='es2015', autocreate_babelrc=True, **kwargs):
        """
        Parameters:
            echmascript_version: The echmascript version to use. Defaults to ``"es2015"``.
            autocreate_babelrc (bool):
            **kwargs: Kwargs for
                :class:`ievv_opensource.utils.ievvbuildstatic.browserify_jsbuild.Plugin`.
        """
        self.echmascript_version = echmascript_version
        self.autocreate_babelrc = autocreate_babelrc
        super(Plugin, self).__init__(**kwargs)

    def install(self):
        """
        Installs the ``babelify`` and ``babel-preset-<echmascript_version kwarg>``
        NPM packages in addition to the packages installed by
        :meth:`ievv_opensource.utils.ievvbuildstatic.browserify_jsbuild.Plugin.install`.

        The packages are installed with no version specified, so you
        probably want to freeze the versions using the
        :class:`ievv_opensource.utils.ievvbuildstatic.npminstall.Plugin` plugin.
        """
        super(Plugin, self).install()
        self.app.get_installer('npm').queue_install(
            'babelify')
        self.app.get_installer('npm').queue_install(
            'babel-preset-{}'.format(self.echmascript_version))

    def get_babel_presets(self):
        """
        Get a list of babelify presets.

        This is the presets that go into ``<HERE>`` in
        ``babelify -t [ babelify --presets [ <HERE> ] ]``.

        Defaults to ``["<the echmascript_version kwarg>"]``.
        """
        presets = [self.echmascript_version]
        return presets

    def get_browserify_extra_args(self):
        return ['-t', '[', 'babelify', ']']

    def get_babelrc_path(self):
        return self.app.get_source_path('.babelrc')

    def babelrc_exists(self):
        return os.path.exists(self.get_babelrc_path())

    def make_babelrc_dict(self):
        return {
            "presets": self.get_babel_presets()
        }

    def create_babelrc(self):
        open(self.get_babelrc_path(), 'w').write(
            json.dumps(
                self.make_babelrc_dict(),
                indent=2,
                sort_keys=True
            ))

    def post_run(self):
        if self.autocreate_babelrc:
            self.create_babelrc()
        elif not self.babelrc_exists():
            self.get_logger().command_error(
                '{babelrc_path} does not exist.'
                'When configured with autocreate_babelrc=False, we expect '
                'you to create the .babelrc.'.format(babelrc_path=self.get_babelrc_path()))
            raise SystemExit()
