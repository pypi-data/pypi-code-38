import json
import os

from ievv_opensource.utils.ievvbuildstatic import pluginbase
from ievv_opensource.utils.ievvbuildstatic.installers.npm import NpmInstaller
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin, ShellCommandError


class CssBuildException(Exception):
    """
    Raised when :meth:`.AbstractPlugin.build_css` fails.
    """


class AbstractPlugin(pluginbase.Plugin, ShellCommandMixin):
    """
    Base class for builders that produce CSS.
    """
    default_group = 'css'

    def __init__(self, lint=True, lintrules=None, lintrules_overrides=None, autoprefix=True,
                 browserslist='> 5%', **kwargs):
        """

        Args:
            lint (bool): Lint the styles? Defaults to ``True``.
            lintrules (dict): Rules for the linter. See https://github.com/stylelint/stylelint.
                Defaults to::

                    {
                        "block-no-empty": None,
                        "color-no-invalid-hex": True,
                        "comment-empty-line-before": ["always", {
                            "ignore": ["stylelint-commands", "after-comment"],
                        }],
                        "declaration-colon-space-after": "always",
                        "indentation": 4,
                        "max-empty-lines": 2
                    }

            lintrules_overrides (dict): Overrides for ``lintrules``. Use this
                if you just want to add new rules or override some of the existing rules.
            autoprefix (bool): Run https://github.com/postcss/autoprefixer on the css?
                Defaults to ``True``.
            browserslist (str): A string with defining supported browsers
                for https://github.com/ai/browserslist. Used by the autoprefix
                and cssnano commands.
            **kwargs: Kwargs for :class:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin`.
        """
        super(AbstractPlugin, self).__init__(**kwargs)
        self.lint = lint
        self.autoprefix = autoprefix
        self.browserslist = browserslist
        self.lintrules = lintrules or {
            "block-no-empty": None,
            "color-no-invalid-hex": True,
            "comment-empty-line-before": ["always", {
                "ignore": ["stylelint-commands", "after-comment"],
            }],
            "declaration-colon-space-after": "always",
            "indentation": 4,
            "max-empty-lines": 2
        }
        if lintrules_overrides:
            self.lintrules.update(lintrules_overrides)

    def get_postcss_cli_version(self):
        return None

    def get_autoprefixer_version(self):
        return None

    def get_cssnano_version(self):
        return None

    def get_stylelint_version(self):
        return None

    def should_minify(self):
        return self.app.apps.is_in_production_mode()

    def requires_postcss(self):
        return self.autoprefix or self.should_minify()

    def install(self):
        if self.requires_postcss():
            self.app.get_installer('npm').queue_install(
                'postcss-cli', version=self.get_postcss_cli_version())
            if self.autoprefix:
                self.app.get_installer('npm').queue_install(
                    'autoprefixer', version=self.get_autoprefixer_version())
            if self.should_minify():
                self.app.get_installer('npm').queue_install(
                    'cssnano', version=self.get_cssnano_version())
        if self.lint:
            self.app.get_installer('npm').queue_install(
                'stylelint', version=self.get_stylelint_version())

    def build_css(self, temporary_directory):
        """
        Override this method and implement the code to build the css.
        """
        raise NotImplementedError()

    def get_destinationfile_path(self):
        """
        Override this method and return the absolute path of the destination/output css
        file.
        """
        raise NotImplementedError()

    def run_postcss(self):
        args = []
        if self.autoprefix:
            args.extend([
                '--use', 'autoprefixer',
                '--autoprefixer.browsers', self.browserslist,
            ])
        if self.should_minify():
            args.extend([
                '--use', 'cssnano',
                '--cssnano.browsers', self.browserslist,
            ])
        self.get_logger().command_start('Running postcss with [{args}] on {destination}'.format(
            args=' '.join(args),
            destination=self.get_destinationfile_path()))
        args.extend([
            '--output', self.get_destinationfile_path(),
            self.get_destinationfile_path()
        ])
        try:
            self.run_shell_command(
                self.app.get_installer('npm').find_executable('postcss'),
                args=args)
        except ShellCommandError:
            self.get_logger().error('postcss failed!')
            raise CssBuildException()
        else:
            self.get_logger().success('postcss ran successfully :)')

    def get_all_source_file_paths(self):
        """
        Used for utilities like the linter to get a list of all
        source files.

        You must override this in subclasses.
        """
        raise NotImplementedError()

    def make_lintconfig_file(self, temporary_directory):
        lintconfig_path = os.path.join(temporary_directory, 'stylelint.json')
        lintconfig = {
            'rules': self.lintrules,
        }
        open(lintconfig_path, 'wb').write(json.dumps(lintconfig, indent=2).encode('utf-8'))
        return lintconfig_path

    def lint_styles(self, temporary_directory):
        lintconfig_path = self.make_lintconfig_file(temporary_directory=temporary_directory)
        self.get_logger().command_start('Linting styles')
        args = [
            self.get_all_source_file_paths()[0],
            '--config', lintconfig_path
        ]
        try:
            self.run_shell_command(
                self.app.get_installer('npm').find_executable('stylelint'),
                args=args)
        except ShellCommandError:
            self.get_logger().error('Stylesheet linting failed!')
        else:
            self.get_logger().success('Stylesheet linting was successful :)')

    def preprocess_styles(self, temporary_directory):
        if self.lint:
            self.lint_styles(temporary_directory=temporary_directory)

    def postprocess_styles(self, temporary_directory):
        if self.requires_postcss():
            self.run_postcss()

    def run(self):
        temporary_directory = self.make_temporary_build_directory()
        try:
            self.preprocess_styles(temporary_directory=temporary_directory)
            self.build_css(temporary_directory=temporary_directory)
            self.postprocess_styles(temporary_directory=temporary_directory)
        except CssBuildException:
            pass
