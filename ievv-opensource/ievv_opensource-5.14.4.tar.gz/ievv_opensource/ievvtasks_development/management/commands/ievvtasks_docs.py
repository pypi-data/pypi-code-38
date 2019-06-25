import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ievv_opensource.ievvtasks_common.open_file import open_file_with_default_os_opener
from ievv_opensource.utils import virtualenvutils
from ievv_opensource.utils.logmixin import Logger, LogMixin
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin, ShellCommandError


class Command(BaseCommand, LogMixin, ShellCommandMixin):
    help = 'Build, open and clean docs (or all at once).'

    def __get_documentation_directory(self):
        default_directory = os.path.join('not_for_deploy', 'docs')
        return getattr(settings, 'IEVVTASKS_DOCS_DIRECTORY', default_directory)

    def __get_documentation_build_directory(self):
        default_build_directory = os.path.join(self.__get_documentation_directory(), '_build')
        return getattr(settings, 'IEVVTASKS_DOCS_BUILD_DIRECTORY', default_build_directory)

    def __get_documentation_indexhtml_path(self):
        return os.path.join(self.__get_documentation_build_directory(), 'index.html')

    def add_arguments(self, parser):
        parser.add_argument('-b', '--build', dest='build_docs',
                            required=False, action='store_true',
                            help='Build the docs.')
        parser.add_argument('-c', '--clean', dest='cleandocs',
                            required=False, action='store_true',
                            help='Remove any existing built docs before building the docs.')
        parser.add_argument('-o', '--open', dest='opendocs',
                            required=False, action='store_true',
                            help='Open the docs after building them.')
        parser.add_argument('--fail-on-warning', dest='fail_on_warning',
                            required=False, action='store_true',
                            help='Fail on warning.')
        parser.add_argument('--buildstatic-docs', dest='include_buildstatic_docs',
                            action='store_false', default=False,
                            help='Include ievv buildstatic docs.')
        parser.add_argument('--loglevel', dest='loglevel',
                            required=False, default='stdout',
                            choices=['debug', 'stdout', 'info', 'warning', 'error'],
                            help='Set loglevel. Can be one of: debug, stdout, info, warning or error '
                                 '(listed in order of verbosity).')
        parser.add_argument('-q', '--quiet', dest='loglevel',
                            required=False, action='store_const', const='warning',
                            help='Quiet output. Same as "--loglevel warning".')
        parser.add_argument('--debug', dest='loglevel',
                            required=False, action='store_const', const='debug',
                            help='Verbose output. Same as "--loglevel debug".')

    def _opendocs(self):
        self.get_logger().info('Opening {} in your browser.'.format(self.indexhtmlpath))
        open_file_with_default_os_opener(self.indexhtmlpath)

    def __clean_docs(self):
        if os.path.exists(self.__get_documentation_build_directory()):
            self.get_logger().debug('Removing {}'.format(self.__get_documentation_build_directory()))
            shutil.rmtree(self.__get_documentation_build_directory())
        else:  # pragma: no cover
            # Excluded from code coverage because this does not happen
            # since we always run tests with a removed build directory.
            self.get_logger().debug('Not removing {} - it does not exist.'.format(
                self.__get_documentation_build_directory()))

    def log_shell_command_stderr(self, line):
        """
        Called by :meth:`.run_shell_command` each time the shell
        command outputs anything to stderr.
        """
        method = 'stderr'
        if 'warning' in line.lower():
            method = 'warning'
        elif 'error' in line.lower():
            method = 'error'
        getattr(self.get_logger(), method)(line.rstrip())

    def get_logger_name(self):
        return 'ievv docs'

    def get_loglevel(self):
        return self.loglevel

    def __build_sphinx_docs(self):
        kwargs = {
            'b': 'html'
        }
        if self.fail_on_warning:  # pragma: no cover
            # Excluded from coverage because testing this would
            # require a complete mock of the docs directory.
            kwargs['W'] = True
            kwargs['T'] = True
        try:
            self.run_shell_command(
                executable='sphinx-build',
                args=[
                    self.__get_documentation_directory(),
                    self.__get_documentation_build_directory(),
                ],
                kwargs=kwargs
            )
        except ShellCommandError:  # pragma: no cover
            # We do not need to show any more errors here - they
            # have already been printed by the _out and _err handlers.
            # Excluded from code coverage because we do not test fail_on_warning
            # as explained above.
            pass

    def __get_buildstatic_documentation_build_directory(self):
        return os.path.join(self.__get_documentation_build_directory(), 'ievvbuildstatic')

    def __build_buildstatic_docs(self):
        settings.IEVVTASKS_BUILDSTATIC_APPS.configure_logging(
            loglevel=self.get_loglevel(),
            command_error_message='Re-run with "--debug" for more details.')
        settings.IEVVTASKS_BUILDSTATIC_APPS.install()
        settings.IEVVTASKS_BUILDSTATIC_APPS.run()
        settings.IEVVTASKS_BUILDSTATIC_APPS.build_docs(
            output_directory=self.__get_buildstatic_documentation_build_directory())

    def handle(self, *args, **options):
        self.loglevel = getattr(Logger, options['loglevel'].upper())
        cleandocs = options['cleandocs']
        build_docs = options['build_docs']
        opendocs = options['opendocs']
        include_buildstatic_docs = options['include_buildstatic_docs']
        self.indexhtmlpath = self.__get_documentation_indexhtml_path()
        self.fail_on_warning = options['fail_on_warning']

        if not (cleandocs or opendocs or build_docs):
            raise CommandError('You must specify at least one of: --build, '
                               '--clean or --open. See --help for more info.')

        if cleandocs and opendocs and not build_docs:
            raise CommandError('Can not use --clean and --open without also using --build.')

        virtualenvutils.add_virtualenv_bin_directory_to_path()
        if cleandocs:
            self.__clean_docs()
        if build_docs:
            self.__build_sphinx_docs()
            if include_buildstatic_docs:
                self.__build_buildstatic_docs()
        if opendocs:
            self._opendocs()
        else:
            self.get_logger().info('Built docs. Use "ievv docs -o" to open them in your browser to view them.')
