# -*- coding: utf-8 -*-
import logging
import os
import re
import sys
import warnings

import click
import sentry_sdk
from missinglink.core.context import init_context2
from missinglink.core.eprint import eprint
from missinglink.sdk.conda_util import is_conda_env, get_conda_channel

from missinglink.commands.http_session import create_http_session
from missinglink.commands.mali_version import MissinglinkVersion
from missinglink.commands.utilities import pip_utils

try:
    from itertools import zip_longest
except ImportError:
    # noinspection PyUnresolvedReferences
    from itertools import izip_longest as zip_longest

__pre_call_hook = None

__PIP_UPDATE_MESSAGE = ["pip install {pip_index} --upgrade {package}"]
__CONDA_UPDATE_MESSAGE = ["conda config --add channels conda-forge", "conda config --add channels {ml_conda_channel}", "conda install {package}"]

__UPDATE_MESSAGE = ["Update is available for missinglink.", "To install, please run:"]


def setup_pre_call(ctx):
    if ctx.obj.log_level is not None:
        __setup_logger_for_stderr(ctx.obj.log_level)

    with sentry_sdk.configure_scope() as cli_scope:
        token_data = ctx.obj.config.token_data

        cli_scope.set_tag('command', ctx.invoked_subcommand)
        cli_scope.user = {'id': token_data.get('uid'), 'email': token_data.get('email'),
                          'username': token_data.get('name')}


def __setup_logger_for_stderr(log_level):
    if not log_level:
        return

    log_level = log_level.upper()

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    handler = logging.StreamHandler(stream=sys.stderr)
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    logging_method = getattr(root_logger, log_level.lower())
    logging_method('log level set to %s (this is a test message)', log_level)


def set_pre_call_hook(pre_call_hook):
    global __pre_call_hook
    __pre_call_hook = pre_call_hook


def token_normalize_func(token):
    convert = {
        'projectId': 'project',
        'project-Id': 'project',
        'experimentId': 'experiment',
        'experiment-id': 'experiment',
        'no_progressbar': 'no-progressbar',
        'noProgressbar': 'no-progressbar',
        'enable_progressbar': 'enable-progressbar',
        'enableProgressbar': 'enable-progressbar',
        'resource_group': 'resource-group',
        'restore_aws_template': 'restore-aws-template',
        'restore_azure_template': 'restore-azure-template',
        'no-gcp': 'no-gcp-link',
        'no-azure': 'no-azure-link'
    }

    def is_camel(s):
        return s != s.lower() and s != s.upper() and "_" not in s

    def convert_camel_case(name):
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1-\2', name)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s1).lower()

    new_token = convert.get(token)

    if new_token is None and is_camel(token):
        new_token = convert_camel_case(token)

    if new_token is not None and not os.environ.get('ML_DISABLE_DEPRECATED_WARNINGS'):
        click.echo('"%s" is deprecated use "%s" instead' % (token, new_token), err=True)

    return new_token or token


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], color=True, token_normalize_func=token_normalize_func)


class Choice2(click.ParamType):
    """The choice type allows a value to be checked against a fixed set of
    supported values.  All of these values have to be strings.
    :param case_sensitive: Set to false to make choices case insensitive.
    Defaults to true.
    See :ref:`choice-opts` for an example.
    """
    name = 'choice2'

    def __init__(self, choices, case_sensitive=False):
        self.choices = choices
        self.case_sensitive = case_sensitive

    def get_metavar(self, param):
        return '[%s]' % '|'.join(self.choices)

    def get_missing_message(self, param):
        return 'Choose from %s.' % ', '.join(self.choices)

    def _normalize_value(self, ctx, value):
        # Match through normalization and case sensitivity
        # first do token_normalize_func, then lowercase
        # preserve original `value` to produce an accurate message in
        # `self.fail`
        if ctx is not None and ctx.token_normalize_func is not None:
            normed_value = ctx.token_normalize_func(value)
            normed_choices = [ctx.token_normalize_func(choice) for choice in self.choices]
        else:
            normed_value = value
            normed_choices = self.choices

        return normed_value, normed_choices

    def _get_normed_choices_value(self, ctx, value):
        normed_value, normed_choices = self._normalize_value(ctx, value)

        if not self.case_sensitive:
            normed_value = normed_value.lower()
            normed_choices = [choice.lower() for choice in normed_choices]

        return normed_value, normed_choices

    def convert(self, value, param, ctx):
        # Exact match
        if value in self.choices:
            return value

        normed_value, normed_choices = self._get_normed_choices_value(ctx, value)

        if normed_value in normed_choices:
            return normed_value

        self.fail('invalid choice: %s. (choose from %s)' % (value, ', '.join(self.choices)), param, ctx)

    def __repr__(self):
        return 'Choice(%r)' % list(self.choices)


def __mute_tqdm_warnings():
    try:
        from tqdm import TqdmSynchronisationWarning

        warnings.filterwarnings('ignore', category=TqdmSynchronisationWarning)
    except ImportError:
        pass


class RewritingGroup(click.Group):
    @staticmethod
    def _match_args(template_list, args):
        for template, arg in zip_longest(template_list, args):
            if not template:
                break
            if not re.match(template, arg or ''):
                return False

        return True

    def parse_args(self, ctx, args):
        super(RewritingGroup, self).parse_args(ctx, args)
        rewrite_map = [
            (('resources', 'install'), ('resources', 'local-grid', 'init')),
            (('aws', 'resource-group'), ('resources', 'group')),
            (('aws', '--region', '.*', 'resource-group'), ('resources', 'group')),
            (('aws',), ('resources', 'aws')),
        ]
        args_list = ctx.protected_args + ctx.args
        for old_cmd, new_cmd in rewrite_map:
            if self._match_args(old_cmd, args_list):
                click.echo('Command ml %s is deprecated, use ml %s' % (' '.join(old_cmd), ' '.join(new_cmd)))
                args_list[:len(old_cmd)] = new_cmd
                ctx.protected_args, ctx.args = args_list[:1], args_list[1:]

        return ctx.args


class _VersionChecker(object):
    @classmethod
    def should_update_ml_version(cls):
        latest_version = cls._get_latest_version(MissinglinkVersion.get_missinglink_package())
        if latest_version is None:
            return False

        current_version = MissinglinkVersion.get_missinglink_cli_version()

        is_dev_version = current_version is None or current_version.startswith('0')
        if is_dev_version:
            return False

        try:
            return cls._version_compare(current_version, latest_version) < 0
        except ValueError:
            return False

    @staticmethod
    def is_staging(package):
        package_keywords = pip_utils.get_keywords(package) or []
        return 'test' in package_keywords

    @classmethod
    def _get_latest_version(cls, package=None, throw_exception=False):
        from missinglink.sdk.conda_util import get_latest_conda_version, is_conda_env

        staging = cls.is_staging(package)

        if is_conda_env():
            latest_version = get_latest_conda_version(package, staging, throw_exception=throw_exception)
        else:
            latest_version = pip_utils.latest_version(package=package, keywords=staging, throw_exception=throw_exception)

        return latest_version

    @staticmethod
    def _version_compare(v1, v2):
        # This will split both the versions by '.'
        arr1 = v1.split(".")
        arr2 = v2.split(".")

        # Initializer for the version arrays
        i = 0

        # We have taken into consideration that both the
        # versions will contains equal number of delimiters
        while i < len(arr1):
            if int(arr2[i]) > int(arr1[i]):
                return -1

            if int(arr1[i]) > int(arr2[i]):
                return 1

            # We can't conclude till now
            i += 1

        # Both the versions are equal
        return 0


@click.group(context_settings=CONTEXT_SETTINGS, cls=RewritingGroup)
@click.option('--output-format', '-o', type=Choice2(['tables', 'json', 'csv', 'json-lines']), default='tables', required=False)
@click.option('--config-prefix', '-cp', envvar='ML_CONFIG_PREFIX', required=False, hidden=True)
@click.option('--config-file', '-cf', envvar='ML_CONFIG_FILE', required=False, hidden=True)
@click.option('--log-level', envvar='ML_LOG_LEVEL', type=Choice2(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']), required=False)
@click.option('--skip-version-check', '-nvc', default=False, is_flag=True, required=False)
@click.option('--disable-interactive', default=False, is_flag=True, required=False, hidden=True)
@click.option('--store-result', default=False, is_flag=True, required=False, hidden=True)
@click.pass_context
def cli(ctx, output_format, config_prefix, config_file, log_level, skip_version_check, disable_interactive, store_result):
    global __pre_call_hook

    __mute_tqdm_warnings()

    init_context2(ctx, create_http_session(), output_format, config_prefix, config_file)

    ctx.obj.log_level = log_level
    ctx.obj.skip_version_check = skip_version_check
    ctx.obj.disable_interactive = disable_interactive
    ctx.obj.store_result = store_result

    if __pre_call_hook is not None:
        __pre_call_hook(ctx)


def _get_update_message():
    upgrade_message = __CONDA_UPDATE_MESSAGE if is_conda_env() else __PIP_UPDATE_MESSAGE

    package = MissinglinkVersion.get_missinglink_package()
    staging = _VersionChecker.is_staging(package)
    pip_index = '--index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple' if staging else ''

    params = {
        'package': package,
        'ml_conda_channel': get_conda_channel(staging),
        'pip_index': pip_index
    }

    return os.linesep.join(__UPDATE_MESSAGE + upgrade_message).format(**params)


@cli.resultcallback()
@click.pass_context
def process_result(ctx, result, **kwargs):
    if ctx.obj.store_result:
        return getattr(ctx.obj, 'result', None)

    if ctx.obj.skip_version_check:
        return

    if not _VersionChecker.should_update_ml_version():
        return

    eprint(_get_update_message())


@cli.command('upgrade')
@click.pass_context
def upgrade_ml(_ctx):
    require_package = MissinglinkVersion.get_missinglink_package()

    from missinglink import install_package

    os.environ['ML_PRINT_UPDATE'] = '1'
    install_package(require_package)


@cli.command('version')
@click.pass_context
def version(_ctx):
    """Print the current version of ml cli."""
    current_version = MissinglinkVersion.get_missinglink_cli_version()

    click.echo(current_version)


@cli.command('boom', hidden=True)
@click.option('--message')
@click.pass_context
def boom(_ctx, message):
    raise Exception(message)


# noinspection PyBroadException
def update_sdk(latest_version, user_path, throw_exception):
    keywords = pip_utils.get_keywords(MissinglinkVersion.get_missinglink_package()) or []

    require_package = '%s==%s' % (MissinglinkVersion.get_missinglink_package(), latest_version)
    p, args = pip_utils.pip_install(pip_utils.get_pip_server(keywords), require_package, user_path)

    if p is None:
        return False

    try:
        std_output, std_err = p.communicate()
    except Exception:
        if throw_exception:
            raise

        logging.exception("%s failed", " ".join(args))
        return False

    rc = p.returncode

    if rc != 0:
        logging.error(
            '%s failed to upgrade to latest version (%s)', MissinglinkVersion.get_missinglink_package(), latest_version)
        logging.error("failed to run %s (%s)\n%s\n%s", " ".join(args), rc, std_err, std_output)
        return False

    logging.info('%s updated to latest version (%s)', MissinglinkVersion.get_missinglink_package(), latest_version)

    return True


def self_update(throw_exception=False):
    current_version = MissinglinkVersion.get_missinglink_cli_version()
    keywords = pip_utils.get_keywords(MissinglinkVersion.get_missinglink_package()) or []

    if current_version is None:
        return

    latest_version = pip_utils.latest_version(keywords, throw_exception=throw_exception, package=MissinglinkVersion.get_missinglink_package())

    if latest_version is None:
        return

    if current_version == latest_version:
        return

    running_under_virtualenv = getattr(sys, 'real_prefix', None) is not None

    if not running_under_virtualenv:
        logging.info(
            'updating %s to version %s in user path', MissinglinkVersion.get_missinglink_package(), latest_version)

    return update_sdk(latest_version, user_path=not running_under_virtualenv, throw_exception=throw_exception)


def add_commands():
    from missinglink.commands import auth_commands, projects_commands, orgs_commands, experiments_commands, code_commands, \
        models_commands, data_commands, run_commands, resources_commands, defaults_commands, install

    cli.add_command(auth_commands)
    cli.add_command(projects_commands)
    cli.add_command(orgs_commands)
    cli.add_command(experiments_commands)
    cli.add_command(code_commands)
    cli.add_command(models_commands)
    cli.add_command(data_commands)
    cli.add_command(run_commands)
    cli.add_command(resources_commands)
    cli.add_command(defaults_commands)
    cli.add_command(install)
