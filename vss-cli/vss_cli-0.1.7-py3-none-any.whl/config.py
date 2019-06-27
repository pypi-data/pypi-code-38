"""Configuration for VSS CLI (vss-cli)."""
from base64 import b64decode, b64encode
import json
import logging
import os
import platform
import shutil
import sys
from typing import Any, Dict, List, Optional, Tuple, Union, cast  # noqa: F401
from uuid import UUID

import click
from click_spinner import spinner
from pick import pick
from pyvss.const import __version__ as pyvss_version
from pyvss.manager import VssManager
from ruamel.yaml import YAML

import vss_cli.const as const
from vss_cli.data_types import ConfigEndpoint, ConfigFile, ConfigFileGeneral
from vss_cli.exceptions import VssCliError
from vss_cli.helper import debug_requests_on, get_hostname_from_url
from vss_cli.utils.emoji import EMOJI_UNICODE
from vss_cli.validators import validate_email, validate_phone_number
import vss_cli.yaml as yaml

_LOGGING = logging.getLogger(__name__)


class Configuration(VssManager):
    """The configuration context for the VSS CLI."""

    def __init__(self, tk: str = '') -> None:
        """Initialize the configuration."""
        super(Configuration, self).__init__(tk)
        self.user_agent = self._default_user_agent(
            extensions=f'pyvss/{pyvss_version}'
        )
        self.verbose = False  # type: bool
        self.default_endpoint_name = None  # type: str
        # start of endpoint settings
        self._endpoint = const.DEFAULT_ENDPOINT  # type: str
        self.base_endpoint = self.endpoint  # type: str
        self.endpoint_name = const.DEFAULT_ENDPOINT_NAME
        # end of endpoint settings
        self.history = const.DEFAULT_HISTORY  # type: str
        self.webdav_server = const.DEFAULT_WEBDAV_SERVER  # type: str
        self.username = None  # type: Optional[str]
        self.password = None  # type: Optional[str]
        self.token = None  # type: Optional[str]
        self.timeout = None  # type: Optional[int]
        self._debug = False  # type: Optional[bool]
        self.showexceptions = False  # type: bool
        self.columns = None  # type: Optional[List[Tuple[str, str]]]
        self.no_headers = False
        self.table_format = None  # type: Optional[str]
        self.sort_by = None
        self.output = None  # type: str
        self.config = None  # type: str
        self.check_for_updates = None  # type: Optional[bool]
        self.check_for_messages = None  # type: Optional[bool]
        self.config_file = None  # type: ConfigFile
        self.spinner = spinner

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        if value:
            debug_requests_on()
        self._debug = value

    @property
    def endpoint(self):
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: str):
        """ Rebuilds API endpoints"""
        self._endpoint = value
        self.base_endpoint = value
        self.api_endpoint = f'{value}/v2'
        self.token_endpoint = f'{value}/auth/request-token'
        if value:
            self.endpoint_name = get_hostname_from_url(
                value, const.DEFAULT_HOST_REGEX
            )

    def set_defaults(self) -> None:
        """Set default configuration settings"""
        _LOGGING.debug('Setting default configuration.')
        for setting, default in const.DEFAULT_SETTINGS.items():
            if getattr(self, setting) is None:
                setattr(self, setting, default)
        _LOGGING.debug(self)

    def get_token(self, user: str = '', password: str = ''):
        self.api_token = super(Configuration, self).get_token(user, password)
        return self.api_token

    def update_endpoints(self, endpoint: str = ''):
        """ Rebuilds API endpoints"""
        self.base_endpoint = endpoint
        self.api_endpoint = f'{endpoint}/v2'
        self.token_endpoint = f'{endpoint}/auth/request-token'

    def echo(self, msg: str, *args: Optional[Any]) -> None:
        """Put content message to stdout."""
        self.log(msg, *args)

    def log(  # pylint: disable=no-self-use
        self, msg: str, *args: Optional[str]
    ) -> None:  # pylint: disable=no-self-use
        """Log a message to stdout."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stdout)

    def secho(self, msg: str, *args: Optional[Any], **kwargs) -> None:
        """Put content message to stdout with style."""
        self.slog(msg, *args, **kwargs)

    def slog(  # pylint: disable=no-self-use
        self, msg: str, *args: Optional[str], **kwargs
    ) -> None:  # pylint: disable=no-self-use
        """Log a message to stdout with style."""
        if args:
            msg %= args
        click.secho(msg, file=sys.stdout, **kwargs)

    def vlog(self, msg: str, *args: Optional[str]) -> None:
        """Log a message only if verbose is enabled."""
        if self.verbose:
            self.log(msg, *args)

    def __repr__(self) -> str:
        """Return the representation of the Configuration."""
        view = {
            "endpoint": self.endpoint,
            "default_endpoint_name": self.default_endpoint_name,
            "endpoint_name": self.endpoint_name,
            "access_token": 'yes' if self.token is not None else 'no',
            "user": 'yes' if self.username is not None else 'no',
            "user_password": 'yes' if self.password is not None else 'no',
            "output": self.output,
            "timeout": self.timeout,
            "debug": self.debug,
            "verbose": self.verbose,
        }

        return "<Configuration({})".format(view)

    def auto_output(self, auto_output: str) -> str:
        """Configure output format."""
        if self.output == "auto":
            if auto_output == 'data':
                auto_output = const.DEFAULT_RAW_OUTPUT
            _LOGGING.debug(f"Setting auto-output to: {auto_output}")
            self.output = auto_output
        return self.output

    @staticmethod
    def get_pip_binary() -> str:
        cmd_bin_opts = ['pip3', 'pip']
        cmd_bin = None
        for cmd_bin_opt in cmd_bin_opts:
            if shutil.which(cmd_bin_opt, mode=os.X_OK):
                cmd_bin = cmd_bin_opt
                return cmd_bin
        # raise if nothing found
        if not cmd_bin:
            raise click.ClickException(
                f"Cloud not find {', '.join(cmd_bin_opts)}"
            )

    @staticmethod
    def _default_user_agent(
        name: str = const.PACKAGE_NAME,
        version: str = const.__version__,
        extensions: str = '',
    ) -> str:
        # User-Agent:
        # <product>/<version> (<system-information>)
        # <platform> (<platform-details>) <extensions>
        user_agent = (
            f'{name}/{version} '
            f'({platform.system()}/{platform.release()}) '
            f'Python/{platform.python_version()} '
            f'({platform.platform()}) {extensions}'
        )
        return user_agent

    def set_credentials(
        self,
        username: str,
        password: str,
        token: str,
        endpoint: str,
        name: str,
    ) -> None:
        self.username = username
        self.password = password
        self.api_token = token
        self.token = token
        self.endpoint = endpoint
        self.endpoint_name = name
        return

    def load_profile_from_config(
        self, endpoint: str = None
    ) -> Tuple[Optional[ConfigEndpoint], Optional[str], Optional[str]]:
        username, password = None, None
        # load from
        config_endpoint = self.config_file.get_endpoint(endpoint)
        if config_endpoint:
            # get auth attr
            auth = config_endpoint[0].auth
            # get token attr
            token = config_endpoint[0].token
            if not auth or not token:
                _LOGGING.warning('Invalid configuration endpoint found.')
            else:
                auth_enc = auth.encode()
                credentials_decoded = b64decode(auth_enc)
                # get user/pass
                username, password = credentials_decoded.split(b':')
            return config_endpoint[0], username, password
        else:
            return None, username, password

    def load_config_file(self, config: str = None) -> Union[ConfigFile, None]:
        raw_config = self.load_raw_config_file(config=config)
        self.config_file = ConfigFile.from_json(raw_config)
        return self.config_file

    def load_raw_config_file(self, config: str = None) -> Union[dict, None]:
        config_file = config or self.config
        try:
            with open(config_file, 'r') as f:
                config_dict = yaml.load_yaml(self.yaml(), f)
                return json.dumps(config_dict)
        except ValueError as ex:
            _LOGGING.error(f'Error loading configuration file: {ex}')
            raise VssCliError(
                'Invalid configuration file.'
                'Run "vss-cli configure mk" or '
                '"vss-cli configure upgrade" to upgrade '
                'legacy configuration.'
            )

    def load_config(self, validate: bool = True):
        try:
            # input configuration check
            if self.token or (self.username and self.password):
                # setting defaults if required
                self.set_defaults()
                _LOGGING.debug(f'Loading from input')
                # don't load config file
                if self.token:
                    _LOGGING.debug(f'Checking token')
                    # set api token
                    self.api_token = self.token
                    return self.username, self.password, self.api_token
                elif self.username and self.password:
                    _LOGGING.debug(f'Checking user/pass to generate token')
                    # generate a new token - won't save
                    _LOGGING.warning(
                        'A new token will be generated but not persisted. '
                        'Consider running command "configure mk" to save your '
                        'credentials.'
                    )
                    self.get_token(self.username, self.password)
                    _LOGGING.debug(f'Token generated {self.api_token}')
                    return self.username, self.password, self.api_token
                else:
                    raise VssCliError(
                        'Environment variables error. Please, verify '
                        'VSS_TOKEN or VSS_USER and VSS_USER_PASS'
                    )
            else:
                _LOGGING.debug(f'Loading configuration file: {self.config}')
                if os.path.isfile(self.config):
                    # load configuration file from json string into class
                    self.config_file = self.load_config_file()
                    # general area
                    if self.config_file.general:
                        _LOGGING.debug(
                            f'Loading general settings from {self.config}'
                        )
                        # set config defaults
                        for setting in const.GENERAL_SETTINGS:
                            try:
                                # check if setting hasn't been set
                                # by input or env
                                # which overrides configuration file
                                if getattr(self, setting) is None:
                                    setattr(
                                        self,
                                        setting,
                                        getattr(
                                            self.config_file.general, setting
                                        ),
                                    )
                                else:
                                    _LOGGING.debug(
                                        f'Prioritizing {setting} from '
                                        f'command line input.'
                                    )
                            except KeyError as ex:
                                _LOGGING.warning(
                                    f'Could not load general setting'
                                    f' {setting}: {ex}'
                                )
                        # printing out
                        _LOGGING.debug(f"General settings loaded: {self}")
                    # load preferred endpoint from file if any
                    if self.config_file.endpoints:
                        _LOGGING.debug(
                            f'Loading endpoint settings from {self.config}'
                        )
                        _LOGGING.debug(
                            f'Looking for endpoint={self.endpoint},'
                            f' default_endpoint_name='
                            f'{self.default_endpoint_name}'
                        )
                        # 1. provided by input
                        if self.endpoint:
                            msg = (
                                f'Cloud not find endpoint provided by '
                                f'input {self.endpoint}. \n'
                            )
                            # load endpoint from endpoints
                            config_endpoint, usr, pwd = self.load_profile_from_config(  # NOQA: E501
                                endpoint=self.endpoint
                            )
                        # 2. provided by configuration file
                        #    (default_endpoint_name)
                        elif self.default_endpoint_name:
                            msg = (
                                f'Could not find default endpoint '
                                f'{self.default_endpoint_name}. \n'
                            )
                            # load endpoint from endpoints
                            config_endpoint, usr, pwd = self.load_profile_from_config(  # NOQA: E501
                                endpoint=self.default_endpoint_name
                            )
                        # 3. fallback to default settings
                        else:
                            msg = (
                                f"Invalid endpoint {self.endpoint_name} "
                                f"configuration. \n"
                            )
                            config_endpoint, usr, pwd = self.load_profile_from_config(  # NOQA: E501
                                endpoint=self.endpoint_name
                            )
                        # check valid creds
                        if not (
                            usr
                            and pwd
                            or getattr(config_endpoint, 'token', None)
                        ):
                            _LOGGING.warning(msg)
                            default_endpoint = const.DEFAULT_ENDPOINT_NAME
                            _LOGGING.warning(
                                f'Falling back to {default_endpoint}'
                            )
                            config_endpoint, usr, pwd = self.load_profile_from_config(  # NOQA: E501
                                endpoint=const.DEFAULT_ENDPOINT_NAME
                            )
                        # set config data
                        self.set_credentials(
                            usr,
                            pwd,
                            config_endpoint.token,
                            config_endpoint.url,
                            config_endpoint.name,
                        )
                        if validate:
                            # last check cred
                            creds = self.username and self.password
                            if not (creds or self.api_token):
                                raise VssCliError(
                                    'Run "vss-cli configure mk" to add '
                                    'endpoint to configuration file or '
                                    '"vss-cli configure upgrade" to upgrade '
                                    'legacy configuration.'
                                )
                            _LOGGING.debug(
                                f'Loaded from file: {self.endpoint_name}: '
                                f'{self.endpoint}:'
                                f': {self.username}'
                            )
                            try:
                                self.whoami()
                                _LOGGING.debug('Token validated successfully.')
                            except Exception as ex:
                                self.vlog(str(ex))
                                _LOGGING.debug('Generating a new token')
                                try:
                                    self.api_token = self.get_token(
                                        self.username, self.password
                                    )
                                    _LOGGING.debug(
                                        'Token generated successfully'
                                    )
                                except Exception as ex:
                                    _LOGGING.warning(
                                        f'Could not generate new token: {ex}'
                                    )
                                endpoint = self._create_endpoint_config(
                                    token=self.api_token
                                )
                                self.write_config_file(new_endpoint=endpoint)
                                # check for updates
                                if self.check_for_updates:
                                    self.check_available_updates()
                                # check for unread messages
                                if self.check_for_messages:
                                    self.check_unread_messages()
                        return self.username, self.password, self.api_token
                else:
                    self.set_defaults()
            raise VssCliError(
                'Invalid configuration. Please, run '
                '"vss-cli configure mk" to initialize configuration, or '
                '"vss-cli configure upgrade" to upgrade legacy '
                'configuration.'
            )
        except Exception as ex:
            raise VssCliError(str(ex))

    def check_available_updates(self) -> None:
        try:
            _LOGGING.debug('Checking for available updates.')
            cmd_bin = self.get_pip_binary()
            # create command with the right exec
            pip_cmd = f'{cmd_bin} list --outdated'.split(None)
            from subprocess import Popen, PIPE

            p = Popen(pip_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            out_decoded = out.decode('utf-8')
            # verify if package name is in outdated string
            pkg_name = const.PACKAGE_NAME
            if pkg_name in out_decoded:
                lines = out_decoded.split('\n')
                pkg_line = [line for line in lines if pkg_name in line]
                if pkg_line:
                    pkg_line = pkg_line.pop()
                    pkg, current, latest, pkgn = pkg_line.split(None)
                    self.secho(
                        f'Update available {current} -> {latest} '
                        f'{EMOJI_UNICODE.get(":upwards_button:")}.',
                        fg='green',
                        nl=False,
                    )
                    self.secho(' Run ', fg='green', nl=False)
                    self.secho('vss-cli upgrade', fg='red', nl=False)
                    self.secho(' to install latest. \n', fg='green')
            else:
                self.secho(
                    f'Running latest version {const.__version__} '
                    f'{EMOJI_UNICODE.get(":white_heavy_check_mark:")}\n',
                    fg='green',
                )
        except Exception as ex:
            _LOGGING.error(f'Could not check for updates: {ex}')

    def check_unread_messages(self) -> None:
        try:
            _LOGGING.debug('Checking for unread messages')
            messages = self.get_user_messages(
                filter='status,eq,Created', per_page=100
            )
            n_messages = len(messages)
            if messages:
                self.secho(
                    f'You have {n_messages} unread messages '
                    f'{EMOJI_UNICODE.get(":envelope_with_arrow:")} ',
                    fg='green',
                    nl=False,
                )
                self.secho('Run ', fg='green', nl=False)
                self.secho(
                    'vss-cli message ls -f status,eq,Created',
                    fg='red',
                    nl=False,
                )
                self.secho(' to list unread messages.', fg='green')
            else:
                _LOGGING.debug('No messages with Created status')
        except Exception as ex:
            _LOGGING.error(f'Could not check for messages: {ex}')

    def _create_endpoint_config(self, token: str = None) -> ConfigEndpoint:
        token = token or self.get_token(self.username, self.password)
        # encode or save
        username = (
            self.username
            if isinstance(self.username, bytes)
            else self.username.encode()
        )
        password = (
            self.password
            if isinstance(self.password, bytes)
            else self.password.encode()
        )
        credentials = b':'.join([username, password])
        auth = b64encode(credentials).strip().decode('utf-8')
        endpoint_cfg = {
            'url': self.base_endpoint,
            'name': self.endpoint_name,
            'auth': auth,
            'token': token,
        }
        return ConfigEndpoint.from_json(json.dumps(endpoint_cfg))

    def load_config_template(self) -> ConfigFile:
        # load template in case it fails
        with open(const.DEFAULT_CONFIG_TMPL, 'r') as f:
            config_tmpl = yaml.load_yaml(self.yaml(), f)
            raw_config_tmpl = json.dumps(config_tmpl)
            config_file_tmpl = ConfigFile.from_json(raw_config_tmpl)
        return config_file_tmpl

    def write_config_file(
        self,
        new_config_file: Optional[ConfigFile] = None,
        new_endpoint: Optional[ConfigEndpoint] = None,
        config_general: Optional[ConfigFileGeneral] = None,
    ) -> bool:
        """
        Creates or updates configuration endpoint section.

        """
        # load template in case it fails
        config_file_tmpl = self.load_config_template()
        try:
            _LOGGING.debug(f'Writing configuration file: {self.config}')
            # validate if file exists
            if os.path.isfile(self.config):
                with open(self.config, 'r+') as fp:
                    try:
                        _conf_dict = yaml.load_yaml(self.yaml(), fp)
                        raw_config = json.dumps(_conf_dict)
                        config_file = ConfigFile.from_json(raw_config)
                    except (ValueError, TypeError) as ex:
                        _LOGGING.warning(f'Invalid config file: {ex}')
                        if click.confirm(
                            f'An error occurred loading the '
                            f'configuration file. '
                            f'Would you like to recreate it?'
                        ):
                            config_file = config_file_tmpl
                        else:
                            return False
                    if new_config_file:
                        config_file.general = new_config_file.general
                        config_file.update_endpoints(
                            *new_config_file.endpoints
                        )
                    # update general config if required
                    if config_general:
                        config_file.general = config_general
                    # update endpoint if required
                    if new_endpoint:
                        # update endpoint
                        config_file.update_endpoint(new_endpoint)
                    # dumping and loading
                    _conf_dict = json.loads(config_file.to_json())
                    fp.seek(0)
                    yaml.dump_yaml(self.yaml(), _conf_dict, stream=fp)
                    fp.truncate()
                _LOGGING.debug(
                    f'Configuration file {self.config} has been updated'
                )
            else:
                if new_config_file:
                    f_type = 'Config file'
                    config_file_dict = json.loads(new_config_file.to_json())
                else:
                    # New configuration file. A new endpoint must be configured
                    f_type = 'Default template'
                    config_endpoint = self._create_endpoint_config()
                    config_file_tmpl.update_endpoint(config_endpoint)
                    # load and dump
                    config_file_dict = json.loads(config_file_tmpl.to_json())
                # write file
                with open(self.config, 'w') as fp:
                    yaml.dump_yaml(self.yaml(), config_file_dict, stream=fp)
                _LOGGING.debug(
                    f'New {f_type} has been written to {self.config}.'
                )
        except IOError as e:
            raise Exception(
                f'An error occurred writing ' f'configuration file: {e}'
            )
        return True

    def configure(
        self,
        username: str,
        password: str,
        endpoint: str,
        replace: Optional[bool] = False,
        endpoint_name: Optional[str] = None,
    ) -> bool:
        self.username = username
        self.password = password
        # update instance endpoints if provided
        self.endpoint = endpoint
        if endpoint_name:
            self.endpoint_name = endpoint_name
        # directory available
        if not os.path.isdir(os.path.dirname(self.config)):
            os.mkdir(os.path.dirname(self.config))
        # config file
        if os.path.isfile(self.config):
            try:
                self.config_file = self.load_config_file()
                # load credentials by endpoint_name
                config_endpoint, e_username, e_password = self.load_profile_from_config(  # NOQA: E501c
                    endpoint=self.endpoint_name
                )
                # profile does not exist
                if not (e_username and e_password and config_endpoint.token):
                    self.echo(
                        f'Endpoint {self.endpoint_name} not found. '
                        f'Creating...'
                    )
                    endpoint_cfg = self._create_endpoint_config()
                    self.write_config_file(new_endpoint=endpoint_cfg)
                # profile exists
                elif e_username and e_password and config_endpoint.token:
                    username = e_username.decode('utf-8') if e_username else ''
                    confirm = replace or click.confirm(
                        f"Would you like to replace existing configuration?\n "
                        f"{self.endpoint_name}:"
                        f"{username}: {config_endpoint.url}"
                    )
                    if confirm:
                        endpoint_cfg = self._create_endpoint_config()
                        self.write_config_file(new_endpoint=endpoint_cfg)
                    else:
                        return False
            except Exception as ex:
                _LOGGING.warning(f'Invalid config file: {ex}')
                confirm = click.confirm(
                    'An error occurred loading the '
                    f'configuration file. '
                    f'Would you like to recreate it?'
                )
                if confirm:
                    endpoint_cfg = self._create_endpoint_config()
                    return self.write_config_file(new_endpoint=endpoint_cfg)
                else:
                    return False
            # feedback
            self.echo(
                f'Successfully configured credentials for ' f'{self.endpoint}.'
            )
        else:
            endpoint_cfg = self._create_endpoint_config()
            self.write_config_file(new_endpoint=endpoint_cfg)
        return True

    def get_vskey_stor(self, **kwargs) -> bool:
        from webdav3 import client as wc

        options = dict(
            webdav_login=self.username,
            webdav_password=self.password,
            webdav_hostname=self.webdav_server,
            verbose=self.verbose,
        )
        self.vskey_stor = wc.Client(options=options)
        return self.vskey_stor.valid()

    def get_vm_by_uuid_or_name(self, uuid_or_name: str) -> List:
        try:
            # is uuid?
            uuid = UUID(uuid_or_name)
            v = self.get_vm(str(uuid))
            if not v:
                raise click.BadArgumentUsage(
                    'uuid should be an existing Virtual Machine ' 'or template'
                )
            return [v]
        except ValueError:
            # not an uuid
            _LOGGING.debug(f'not an uuid {uuid_or_name}')
            # If it's a value error, then the string
            # is not a valid hex code for a UUID.
            # get vm by name
            g_vms = self.get_vms()
            uuid_or_name = uuid_or_name.lower()
            v = list(
                filter(lambda i: uuid_or_name in i['name'].lower(), g_vms)
            )
            if not v:
                raise click.BadParameter(f'{uuid_or_name} could not be found')
            v_count = len(v)
            if v_count > 1:
                msg = f"Found {v_count} matches. Please select one:"
                sel, index = pick(
                    title=msg,
                    indicator='=>',
                    options=[f"{i['uuid']} ({i['name']})" for i in v],
                )
                return [v[index]]
            return v

    def get_domain_by_name_or_moref(self, name_or_moref: str) -> List[Any]:
        g_domains = self.get_domains()
        name_or_moref = name_or_moref.lower()
        d = list(
            filter(lambda i: name_or_moref in i['name'].lower(), g_domains)
        ) or list(filter(lambda i: name_or_moref in i['moref'], g_domains))
        if not d:
            raise click.BadParameter(f'{name_or_moref} could not be found')
        d_count = len(d)
        if d_count > 1:
            msg = f"Found {d_count} matches. Please select one:"
            sel, index = pick(
                title=msg,
                indicator='=>',
                options=[f"{i['name']} ({i['moref']})" for i in d],
            )
            return [d[index]]
        return d

    def get_network_by_name_or_moref(self, name_or_moref: str) -> List[Any]:
        g_networks = self.get_networks(sort='name')
        name_or_moref = name_or_moref.lower()
        # search by name or moref
        n = list(
            filter(lambda i: name_or_moref in i['name'].lower(), g_networks)
        ) or list(
            filter(lambda i: name_or_moref in i['moref'].lower(), g_networks)
        )
        if not n:
            raise click.BadParameter(f'{name_or_moref} could not be found')
        net_count = len(n)
        if net_count > 1:
            msg = f"Found {net_count} matches. Please select one:"
            sel, index = pick(
                title=msg,
                indicator='=>',
                options=[f"{i['name']} ({i['moref']})" for i in n],
            )
            return [n[index]]
        return n

    def get_folder_by_name_or_moref_path(
        self, name_moref_path: str
    ) -> List[Any]:
        g_folders = self.get_folders(sort='path', summary=1)
        # search by name or moref
        name_moref_path = name_moref_path.lower()
        f = (
            list(
                filter(
                    lambda i: name_moref_path in i['name'].lower(), g_folders
                )
            )
            or list(
                filter(
                    lambda i: name_moref_path in i['path'].lower(), g_folders
                )
            )
            or list(
                filter(
                    lambda i: name_moref_path in i['moref'].lower(), g_folders
                )
            )
        )

        if not f:
            raise click.BadParameter(f'{name_moref_path} could not be found')
        f_count = len(f)
        if f_count > 1:
            msg = f"Found {f_count} matches. Please select one:"
            sel, index = pick(
                title=msg,
                indicator='=>',
                options=[f"{i['path']} ({i['moref']})" for i in f],
            )
            return [f[index]]
        return f

    def get_os_by_name_or_guest(self, name_or_guest: str) -> List[Any]:
        g_os = self.get_os(sort='guestFullName,desc', per_page=200)
        try:
            o_f = list(filter(lambda i: int(name_or_guest) == i['id'], g_os))
        except ValueError:
            # not an integer
            _LOGGING.debug(f'not an id {name_or_guest}')
            name_or_guest = name_or_guest.lower()
            o_f = list(
                filter(lambda i: name_or_guest in i['guestId'].lower(), g_os)
            ) or list(
                filter(
                    lambda i: name_or_guest in i['guestFullName'].lower(), g_os
                )
            )
        if not o_f:
            raise click.BadParameter(f'{name_or_guest} could not be found')
        o_count = len(o_f)
        if o_count > 1:
            msg = f"Found {o_count} matches. Please select one:"
            sel, index = pick(
                title=msg,
                indicator='=>',
                options=[
                    f"{i['guestFullName']} ({i['guestId']})" for i in o_f
                ],
            )
            return [o_f[index]]
        return o_f

    def get_vss_service_by_name_label_or_id(
        self, name_label_or_id: Union[str, int]
    ) -> List[Any]:
        vss_services = self.get_vss_services(show_all=True, per_page=200)
        try:
            svc_id = int(name_label_or_id)
            svc_ref = list(filter(lambda i: i['id'] == svc_id, vss_services))
        except ValueError as ex:
            # not an integer
            _LOGGING.debug(f'not an id {name_label_or_id} ({ex})')
            # checking name or label
            svc = str(name_label_or_id).lower()
            svc_ref = list(
                filter(lambda i: svc in i['name'].lower(), vss_services)
            ) or list(
                filter(lambda i: svc in i['label'].lower(), vss_services)
            )
        # check if there's no ref
        if not svc_ref:
            raise click.BadParameter(f'{name_label_or_id} could not be found')
        # count for dup results
        o_count = len(svc_ref)
        if o_count > 1:
            msg = f"Found {o_count} matches. Please select one:"
            sel, index = pick(
                title=msg,
                indicator='=>',
                options=[f"{i['label']}" for i in svc_ref],
            )
            return [svc_ref[index]]
        return svc_ref

    def get_iso_by_name_or_guest(
        self, name_or_path_or_id: Union[str, int]
    ) -> List[Any]:
        user_isos = self.get_user_isos()
        pub_isos = self.get_isos(show_all=True, per_page=200)
        try:
            iso_id = int(name_or_path_or_id)
            # public or user
            iso_ref = list(
                filter(lambda i: i['id'] == iso_id, pub_isos)
            ) or list(filter(lambda i: i['id'] == iso_id, user_isos))
        except (ValueError, TypeError) as ex:
            # not an integer
            _LOGGING.debug(f'not an id {name_or_path_or_id} ({ex})')
            # checking name or path
            # check in public and user isos
            iso = str(name_or_path_or_id)
            iso = iso.lower()
            iso_ref = (
                list(filter(lambda i: iso in i['name'].lower(), pub_isos))
                or list(filter(lambda i: iso in i['path'].lower(), pub_isos))
                or list(filter(lambda i: iso in i['name'].lower(), user_isos))
                or list(filter(lambda i: iso in i['path'].lower(), user_isos))
            )
        # check if there's no ref
        if not iso_ref:
            raise click.BadParameter(
                f'{name_or_path_or_id} could not be found'
            )
        # count for dup results
        o_count = len(iso_ref)
        if o_count > 1:
            msg = f"Found {o_count} matches. Please select one:"
            sel, index = pick(
                title=msg,
                indicator='=>',
                options=[f"{i['name']}" for i in iso_ref],
            )
            return [iso_ref[index]]
        return iso_ref

    def get_vm_image_by_name_or_id_path(
        self, name_or_path_or_id: Union[str, int]
    ) -> List[Any]:
        user_imgs = self.get_user_vm_images()
        pub_imgs = self.get_images(show_all=True, per_page=200)
        try:
            img_id = int(name_or_path_or_id)
            # public or user
            img_ref = list(
                filter(lambda i: i['id'] == img_id, pub_imgs)
            ) or list(filter(lambda i: i['id'] == img_id, user_imgs))
        except ValueError as ex:
            # not an integer
            _LOGGING.debug(f'not an id {name_or_path_or_id} ({ex})')
            # checking name or path
            # check in public and user img
            img = str(name_or_path_or_id)
            img = img.lower()
            img_ref = (
                list(filter(lambda i: img in i['name'].lower(), pub_imgs))
                or list(filter(lambda i: img in i['path'].lower(), pub_imgs))
                or list(filter(lambda i: img in i['name'].lower(), user_imgs))
                or list(filter(lambda i: img in i['path'].lower(), user_imgs))
            )
        # check if there's no ref
        if not img_ref:
            raise click.BadParameter(
                f'{name_or_path_or_id} could not be found'
            )
        # count for dup results
        o_count = len(img_ref)
        if o_count > 1:
            msg = f"Found {o_count} matches. Please select one:"
            sel, index = pick(
                title=msg,
                indicator='=>',
                options=[f"{i['name']}" for i in img_ref],
            )
            return [img_ref[index]]
        return img_ref

    def get_cli_spec_from_api_spec(
        self, payload: dict, template: dict
    ) -> dict:
        os_q = self.get_os(filter=f"guestId,eq,{payload.get('os')}")
        machine_os = os_q[0]['guestFullName'] if os_q else payload.get('os')
        fo_q = self.get_folder(payload.get('folder'))
        machine_folder = fo_q['path'] if fo_q else payload.get('folder')
        template['built'] = payload.get('built_from')
        template['machine']['name'] = payload.get('name')
        template['machine']['os'] = machine_os
        template['machine']['cpu'] = payload.get('cpu')
        template['machine']['memory'] = payload.get('memory')
        template['machine']['folder'] = machine_folder
        template['machine']['disks'] = payload.get('disks')
        template['networking']['interfaces'] = [
            {'network': self.get_network(v)['name']}
            for v in payload.get('networks')
        ]
        template['metadata']['billing'] = payload.get('bill_dept')
        template['metadata']['description'] = payload.get('description')
        template['metadata']['usage'] = payload.get('usage')
        template['metadata']['inform'] = payload.get('inform')
        template['metadata']['admin'] = {
            'name': payload.get('admin_name'),
            'email': payload.get('admin_email'),
            'phone': payload.get('admin_phone'),
        }
        template['metadata']['vss_service'] = payload.get('vss_service')
        template['metadata']['vss_options'] = payload.get('vss_options')
        return template

    def get_api_spec_from_cli_spec(self, payload: dict, built: str) -> dict:
        try:
            spec_payload = dict()
            # sections
            machine_section = payload['machine']
            networking_section = payload['networking']
            metadata_section = payload['metadata']
            if built == 'os_install':
                # machine section parse and update
                spec_payload.update(machine_section)
                # replace with valid values
                spec_payload['os'] = self.get_os_by_name_or_guest(
                    machine_section['os']
                )[0]['guestId']
                spec_payload['iso'] = self.get_iso_by_name_or_guest(
                    machine_section['iso']
                )[0]['path']
                # folder
                spec_payload['folder'] = self.get_folder_by_name_or_moref_path(
                    machine_section['folder']
                )[0]['moref']
                # networking
                spec_payload['networks'] = [
                    self.get_network_by_name_or_moref(n['network'])[0]['moref']
                    for n in networking_section['interfaces']
                ]
                # metadata section
                spec_payload.update(metadata_section)
                spec_payload['built'] = built
                spec_payload['bill_dept'] = metadata_section['billing']
                # optional
                if 'inform' in metadata_section:
                    spec_payload['inform'] = [
                        validate_email(None, 'inform', i)
                        for i in metadata_section['inform']
                    ]
                if 'vss_service' in metadata_section:
                    service = self.get_vss_service_by_name_label_or_id(
                        metadata_section['vss_service']
                    )[0]['id']
                    spec_payload['vss_service'] = service
                if 'admin' in metadata_section:
                    admin_name = metadata_section['admin']['name']
                    admin_email = metadata_section['admin']['email']
                    admin_phone = metadata_section['admin']['phone']
                    if admin_name and admin_email and admin_phone:
                        validate_email(None, '', admin_email)
                        validate_phone_number(None, '', admin_phone)
                    spec_payload['admin'] = (
                        f"{admin_name}:" f"{admin_phone}:{admin_email}"
                    )
            return spec_payload
        except KeyError as ex:
            raise click.BadParameter(f'Invalid CLI specification: {ex}')

    def yaml(self) -> YAML:
        """Create default yaml parser."""
        if self:
            return yaml.yaml()

    def yaml_load(self, source: str) -> Any:
        """Load YAML from source."""
        return self.yaml().load(source)

    def yaml_dump(self, source: Any) -> str:
        """Dump dictionary to YAML string."""
        return cast(str, yaml.dump_yaml(self.yaml(), source))

    def yaml_dump_stream(
        self, data: Any, stream: Any = None, **kw: Any
    ) -> Optional[str]:
        return yaml.dump_yaml(self.yaml(), data, stream, **kw)
