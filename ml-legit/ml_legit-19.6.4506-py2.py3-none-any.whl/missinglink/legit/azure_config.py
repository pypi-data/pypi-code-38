# -*- coding: utf-8 -*-
import logging
import os
import re

try:
    # noinspection PyPep8Naming
    import ConfigParser as configparser
except ImportError:
    # noinspection PyUnresolvedReferences
    import configparser


logger = logging.getLogger(__name__)


_azure_logs_muted = False


def _mute_azure_logs():
    global _azure_logs_muted

    if _azure_logs_muted:
        return

    def mute_log(name, level):
        azure_logger = logging.getLogger(name)
        if azure_logger.level == 0:
            azure_logger.setLevel(level)

    mute_log('azure.storage.common.storageclient', logging.WARNING)
    mute_log('msrestazure.azure_active_directory', logging.ERROR)

    _azure_logs_muted = True


def create_storage_client(credentials, subscription_id):
    from azure.mgmt.storage import StorageManagementClient

    return StorageManagementClient(credentials, subscription_id)


def get_access_key_using_msi(storage_account_name):
    _mute_azure_logs()

    logger.debug('get_access_key_using_msi %s', storage_account_name)

    from msrestazure.azure_active_directory import MSIAuthentication

    if not storage_account_name:
        raise ValueError('invalid storage account name')

    role_id = os.environ.get('ML_INSTANCE_ROLE')

    if not role_id:
        raise ValueError('ML_INSTANCE_ROLE environment variable not set')

    def get_resource_group_name():
        rg = r'resourceGroups\/([\w-]*)/'
        storage_accounts = list(storage_client.storage_accounts.list())
        logger.debug('azure storage_accounts %s', storage_accounts)

        for item in storage_accounts:
            if item.name.lower() != storage_account_name.lower():
                continue

            m = re.search(rg, item.id)
            return m.group(1)

    if '/' in role_id:
        subscription_id_parts = role_id.split('/', 3)
        if len(subscription_id_parts) < 2:
            raise ValueError('invalid ML_INSTANCE_ROLE format %s', role_id)

        subscription_id = subscription_id_parts[2]
    else:
        subscription_id = role_id

    credentials = MSIAuthentication(msi_res_id=role_id)
    storage_client = create_storage_client(credentials, subscription_id)

    resource_group_name = get_resource_group_name()

    if not resource_group_name:
        raise ValueError('resource group not found')

    keys_res = storage_client.storage_accounts.list_keys(resource_group_name, storage_account_name)

    logger.debug('azure keys %s', keys_res)

    storage_key = keys_res.keys[0].value if keys_res and len(keys_res.keys) > 0 else None

    if not storage_key:
        raise ValueError('storage key not found')

    return storage_key


class AzureConfig(object):
    _AZURE_DIRECTORY = '.azure'

    def __init__(self):
        self._parser = None

    @classmethod
    def get_config_path(cls):
        if os.name == 'nt':
            return os.path.join(os.environ['USERPROFILE'], cls._AZURE_DIRECTORY)

        return os.path.join(os.path.expanduser('~'), cls._AZURE_DIRECTORY)

    @classmethod
    def get_default_config_path(cls):
        return os.path.join(cls.get_config_path(), 'config')

    @property
    def storage_account(self):
        return self._read_config('storage', 'account')

    @property
    def storage_key(self):
        return self._read_config('storage', 'key')

    def _create_parser_if_needed(self):
        if self._parser is not None:
            return

        default_config = self.get_default_config_path()
        parser = configparser.ConfigParser()
        parser.read(default_config)

        self._parser = parser

    @classmethod
    def set_storage_key_env_var(cls, storage_key):
        os.environ['AZURE_STORAGE_KEY'] = storage_key

    def _read_config(self, section, name):
        self._create_parser_if_needed()

        env_var_name = 'AZURE_{section}_{name}'.format(section=section, name=name)

        value = os.environ.get(env_var_name.upper())

        if value is not None:
            return value

        try:
            return self._parser.get(section, name)
        except (configparser.NoOptionError, configparser.NoSectionError):
            return None


_mute_azure_logs()
