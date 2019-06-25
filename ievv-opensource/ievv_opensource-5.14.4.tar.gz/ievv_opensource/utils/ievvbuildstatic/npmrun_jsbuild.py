from ievv_opensource.utils.ievvbuildstatic import pluginbase
from ievv_opensource.utils.ievvbuildstatic.filepath import AbstractDjangoAppPath
from ievv_opensource.utils.ievvbuildstatic.watcher import ProcessWatchConfig
from ievv_opensource.utils.shellcommandmixin import ShellCommandError
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin


class Plugin(pluginbase.Plugin, ShellCommandMixin):
    """
    Webpack builder plugin.

    Examples:

        Simple example::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.npmrun_jsbuild.Plugin(),
                    ]
                )
            )

        Webpack example::

            Install webpack:

            $ yarn add webpack

            Add the following to your package.json:

                {
                    ...
                    "scripts": {
                        ...
                        "jsbuild": "webpack --config webpack.config.js",
                        "jsbuild-production": "webpack --config webpack.config.js -p"
                        ...
                    }
                    ...
                }

            Create a webpack.config.js with something like this:

                let path = require('path');

                const isProduction = process.env.IEVV_BUILDSTATIC_MODE == 'production';
                const appconfig = require("./ievv_buildstatic.appconfig.json");
                console.log(isProduction);
                console.log(appconfig);

                let webpackConfig = {
                    entry: './scripts/javascript/ievv_jsbase/ievv_jsbase_core.js',
                    output: {
                        filename: 'ievv_jsbase_core.js',
                        path: path.resolve(appconfig.destinationfolder, 'scripts')
                    },
                    module: {
                        loaders: [
                            {
                                test: /.jsx?$/,
                                loader: 'babel-loader',
                                // exclude: /node_modules/
                                include: [
                                    path.resolve(__dirname, "scripts/javascript/ievv_jsbase"),
                                ]
                            }
                        ]
                    }
                };

                if(isProduction) {
                    webpackConfig.devtool = 'source-map';
                } else {
                    webpackConfig.devtool = 'cheap-module-eval-source-map';
                    webpackConfig.output.pathinfo = true;
                }

                module.exports = webpackConfig;

    """
    name = 'npmrun_jsbuild'
    default_group = 'js'

    def __init__(self,
                 extra_import_paths=None,
                 **kwargs):
        super(Plugin, self).__init__(**kwargs)
        self.extra_import_paths = extra_import_paths or []

    @property
    def destinationfolder(self):
        return self.app.get_destination_path('scripts')

    def get_default_import_paths(self):
        return []

    def get_import_paths(self):
        return self.get_default_import_paths() + self.extra_import_paths

    def _get_import_paths_as_strlist(self):
        import_paths = []
        for path in self.get_import_paths():
            if isinstance(path, AbstractDjangoAppPath):
                path = path.abspath
            import_paths.append(path)
        return import_paths

    def install(self):
        self.app.add_pluginconfig_to_json_config(
            plugin_name=self.name,
            config_dict={
                'import_paths': self._get_import_paths_as_strlist()
            }
        )

    def get_npm_script(self):
        if self.app.apps.is_in_production_mode():
            return 'jsbuild-production'
        else:
            return 'jsbuild'

    def get_npm_watch_script(self):
        return 'jsbuild-watch'

    def run(self):
        npm_script = self.get_npm_script()
        about = '"npm run {npm_script}" for {appname!r}'.format(
            npm_script=npm_script,
            appname=self.app.appname
        )
        self.get_logger().command_start('Running {about}'.format(
            about=about))
        try:
            self.run_shell_command('npm',
                                   args=['run', npm_script],
                                   _cwd=self.app.get_source_path())
        except ShellCommandError:
            self.get_logger().command_error('{} FAILED!'.format(about))
        else:
            self.get_logger().command_success('{} succeeded :)'.format(about))

    def __str__(self):
        return '{}({})'.format(super(Plugin, self).__str__(), self.sourcefolder)

    def run_watcher_process(self):
        about = '"npm run {scriptname}" for {appname!r}'.format(
            scriptname=self.get_npm_watch_script(),
            appname=self.app.appname)
        self.get_logger().info(
            'Starting watcher process: {about}.'.format(about=about))
        try:
            self.app.get_installer('npm').run_packagejson_script(script=self.get_npm_watch_script())
        except ShellCommandError:
            self.get_logger().command_error('{} FAILED!'.format(about))
        except KeyboardInterrupt:
            pass

    def watch(self):
        if self.app.get_installer('npm').has_npm_script(self.get_npm_watch_script()):
            return ProcessWatchConfig(
                plugin=self)
        else:
            return None
