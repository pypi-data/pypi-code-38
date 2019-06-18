import os
import errno
import logging
import simplejson as json
from jinja2 import Template
from deployv.helpers import json_helper, utils
from deployv.base.errors import ParameterError
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

_logger = logging.getLogger(__name__)


class DeployvConfig(object):

    def __init__(self, worker_config=None, deploy_config=None, load_defaults=True):
        self._extras = {}
        self.postgres = {}
        self.deployer = {}
        self.http = {}
        self.rmq = {}
        self.instance_config = {}
        self.container_config = {}
        self.maintenance_page = {}
        self.worker_config = self.parse_config(worker_config)
        self._deploy_config = deploy_config or {}
        self.generate_configuration(self._deploy_config, load_defaults=load_defaults)

    def __getattr__(self, name):
        return self._extras.get(name, False)

    def check_config(self, command):
        required_params = {
            'create': ['_deploy_config'],
            'deactivate': ['_deploy_config'],
            'restore': ['_deploy_config'],
            'backup': ['_deploy_config'],
            'deactivate_backup': ['_deploy_config', 'temp_folder', 'prefix'],
            'updatedb': ['_deploy_config'],
            'update_production': ['backup_src', 'compressed_backup_size',
                                  'decompressed_backup_size', 'temp_folder'],
            'build_image': ['_deploy_config'],
        }
        missing_params = []
        if command not in required_params.keys():
            return
        for param in required_params.get(command):
            checker_method = '_check_' + param
            checker_res = True
            value = (getattr(self, param) if hasattr(self, param) else
                     self._extras.get(param, False))
            func = getattr(self, checker_method)
            if func:
                checker_res = func(value)
            if not value or not checker_res:
                missing_params.append(param)
        if missing_params:
            raise ParameterError(
                'Some required parameters are missing, were provided in a wrong'
                ' format or failed a check for the {cmd} command: {params}'
                .format(cmd=command, params=','.join(missing_params)))

    def _check_backup_src(self, backup_src):
        if not os.access(backup_src, os.F_OK | os.R_OK | os.W_OK):
            _logger.error('Unable to write data in the specified backup directory.')
            return False
        return True

    def _check_compressed_backup_size(self, compressed_backup_size):
        parsed_compressed = utils.parse_backup_size(compressed_backup_size)
        if not compressed_backup_size or not parsed_compressed:
            return False
        return True

    def _check_decompressed_backup_size(self, decompressed_backup_size):
        parsed_decompressed = utils.parse_backup_size(decompressed_backup_size)
        if not decompressed_backup_size or not parsed_decompressed:
            return False
        return True

    def _get_backup_src(self, config):
        backup_src = config['group_config'].get('backup_src') or utils.get_backup_src(
            self._deploy_config, self.worker_config)
        return os.path.expanduser(backup_src) if backup_src else False

    def _get_temp_folder(self, config):
        temp_folder = (config['group_config'].get('temp_folder') or
                       self.worker_config.has_option('deployer', 'temp_folder') and
                       self.worker_config.get('deployer', 'temp_folder') or '/tmp')
        res = utils.makedir(temp_folder)
        return res

    def _get_prefix(self, config):
        prefix = config['group_config'].get('prefix') or self._deploy_config.get(
            'instance', {}).get('prefix')
        return prefix

    def _get_compressed_backup_size(self, config):
        compressed_backup_size = config['group_config'].get('compressed_backup_size')
        decompressed_backup_size = config['group_config'].get('decompressed_backup_size')
        parsed_decompressed = utils.parse_backup_size(decompressed_backup_size)
        if not compressed_backup_size and (decompressed_backup_size and parsed_decompressed):
            compressed_value = parsed_decompressed['size_value'] * 0.75
            compressed_unit = parsed_decompressed['size_unit']
            compressed_backup_size = '{size}{unit}'.format(size=compressed_value,
                                                           unit=compressed_unit)
        return compressed_backup_size

    def parse_config(self, additional_config_file=None):
        """Loads and returns the parsed config files in a ConfigParser object.

        The config files are loaded in this order:

        1. /etc/deployv/deployv.conf
        2. /etc/deployv/conf.d/*.conf
        3. ~/.config/deployv/deployv.conf
        4. ~/.config/deployv/conf.d/*.conf
        5. All files received in additional_config_files.

        :param additional_config_file: Additional .conf file to load.
        :type additional_config_files: String

        :returns: The parsed config files.
        :rtype: ConfigParser
        """
        config = self.worker_config or ConfigParser()
        default_config_file = os.path.join(os.path.dirname(__file__),
                                           '../config/deployv.conf')
        config_files = [default_config_file]
        main_dirs = ['/etc/deployv', os.path.expanduser('~/.config/deployv')]
        for main_dir in main_dirs:
            main_config_file = os.path.join(main_dir, 'deployv.conf')
            if os.access(main_config_file, os.F_OK):
                config_files.append(main_config_file)
            addons_dir = os.path.join(main_dir, 'conf.d')
            if os.path.isdir(addons_dir):
                for filename in os.listdir(addons_dir):
                    filepath = os.path.join(addons_dir, filename)
                    if os.path.isfile(filepath) and filename.endswith('.conf'):
                        config_files.append(filepath)
        if len(config_files) == 1:
            _logger.warn("Warning: no config file detected in the config "
                         "paths. You can create a `deployv.conf` file in "
                         "`/etc/deployv/` or `~/.config/deployv/` paths. "
                         "You can also run `deployvcmd setup_config` to "
                         "automatically create the config files for you.")
        if additional_config_file:
            config_files.append(additional_config_file)
        if config_files:
            _logger.info("Loading config files: %s", ", ".join(config_files))
            loaded_files = config.read(config_files)
            if len(config_files) != len(loaded_files):
                _logger.warn("Error loading config files: %s",
                             ", ".join(set(config_files) - set(loaded_files)))
        self.set_worker_config_sections(config)
        return config

    def set_worker_config_sections(self, config):
        """ Sets each section of the worker configuration as an attribute of the config object,
        each attribute will contain a dictionary with the keys of that section. This is so we
        can access to all the configuration in an easier way.

        :param config: Worker configuration
        :type config: ConfigParser object
        """
        booleans = ['use_template', 'use_nginx', 'rmq_ssl']
        integers = ['db_port', 'workers', 'max_instances', 'jobs', 'rmq_port', 'rmq_timeout']
        if not isinstance(config, ConfigParser):
            raise ParameterError('worker_config: Invalid type {}'.format(type(config)))
        for section in config.sections():
            values = dict(config.items(section))
            try:
                for key in values.keys():
                    if key in booleans:
                        values.update({key: config.getboolean(section, key)})
                    elif key in integers:
                        values.update({key: config.getint(section, key)})
            except ValueError as error:
                error_msg = utils.get_error_message(error)
                _logger.error('Failed to parse the parameter `%s` of the section `%s`, %s',
                              key, section, error_msg)
                raise ParameterError('worker_config > {sect} > {key}: Invalid type {t}'
                                     .format(sect=section, key=key, t=type(values.get(key))))
            setattr(self, section, values)

    def generate_configuration(self, config, load_defaults=True):
        """ Configures the current instance of this class with the provided config dict.
        This method sets the `instance_config` and the  `container_config` attributes
        based on the `instance` and `container_config` keys in the config dict, it
        also adds an attribute for each key in the `group_config` key. Each one of these params
        can have a `_get_{attribute name}` method with special logic to help this method decide
        what value will be stored in that new attribute. Note: These `_get_*` methods **must**
        receive the full config dictionary because some special attributes depend on other values.

        :param config: Configuration that will be used to prepare this object to be used by deployv
        :type config: dict
        :param load_defaults: Wether this method will load the default configuration json or not.
        Default: True
        :type load_defaults: bool
        """
        parsed_config = json_helper.load_json(config)
        if not isinstance(parsed_config, dict):
            raise ParameterError('deploy_config: Invalid type: {tp}'.format(tp=type(config)))
        if load_defaults:
            parsed_config = utils.merge_config(parsed_config)
        res = json.loads(Template(json.dumps(parsed_config)).render(parsed_config))
        # Parameters that require extra logic before setting them
        special_params = ['backup_src', 'temp_folder', 'prefix', 'compressed_backup_size']
        self._deploy_config = res
        self.instance_config = res.get('instance') or {}
        self.container_config = res.get('container_config') or {}
        self.maintenance_page = res.get('maintenance_page') or {}
        # Use a copy instead of the original dictionary so we don't alter the original
        # config, this will allow us to update the properties without the params that
        # were previously set
        extras = res.get('group_config', {}).copy()
        for param in special_params:
            get_method = '_get_' + param
            func = getattr(self, get_method)
            if func:
                new_val = func(res)
            else:
                raise ParameterError('The attribute {param} was defined as a special'
                                     ' attribute but the expected `_get_{param}()` method was'
                                     ' not found'.format(param=param))
            extras.update({param: new_val})
        self._extras = extras

    def update_configuration(self, worker_config=False, deploy_config=False):
        """ Updates the configuration of the object based on the provided parameters.
        This will help us update the properties of the object in case we modify the
        deploy config or the worker config or we can specify new configurations to
        replace the current ones.

        :param worker_config: Optional worker configuration object, if specified
        it will override the worker_config property and the new properties will
        be generated based on this new config.
        :type worker_config: ConfigParser() object

        :param deploy_config: Optional deploy configuration, if specified
        it will override the _deploy_config property and the new properties will
        be generated based on this new config. This configuration can be the path
        to the json file, the json string or a dictionary.
        :type deploy_config: String
        """
        self.worker_config = worker_config or self.worker_config
        self.set_worker_config_sections(self.worker_config)
        deploy_config = deploy_config or self._deploy_config
        self.generate_configuration(deploy_config)

    def setup_config_dirs(self):
        _logger.info("Writing config files")
        default_config_file = os.path.join(os.path.dirname(__file__),
                                           '../config/deployv.conf')
        for main_dir in ['/etc/deployv', os.path.expanduser('~/.config/deployv')]:
            config_file_name = os.path.join(main_dir, 'deployv.conf')
            error_msg = "Couldn't write config file: '%s' (skipped)"
            addon_dir = os.path.join(main_dir, 'conf.d')
            is_user_dir = os.path.expanduser('~/') in main_dir
            try:
                os.makedirs(addon_dir)
            except OSError as error:
                if error.errno != errno.EEXIST:
                    _logger.warn(error_msg, config_file_name)
                    continue
            else:
                if is_user_dir:
                    for path in [main_dir.replace('/deployv', ''), main_dir, addon_dir]:
                        self._fix_ownership(path)
            config = ConfigParser()
            config.read([default_config_file, config_file_name])
            try:
                with open(config_file_name, 'w+') as config_file:
                    config.write(config_file)
            except (OSError, IOError):
                _logger.warn(error_msg, config_file_name)
            else:
                _logger.info("Created config file: '%s'", config_file_name)
                if is_user_dir:
                    self._fix_ownership(config_file_name)
        self.worker_config = self.parse_config()

    def _fix_ownership(self, path):
        uid = os.environ.get('SUDO_UID')
        gid = os.environ.get('SUDO_GID')
        if uid is not None:
            os.chown(path, int(uid), int(gid))


def get_config(config_file=None):
    config = DeployvConfig(worker_config=config_file)
    return config.worker_config
