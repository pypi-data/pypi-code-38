# -*- coding: utf-8 -*-
import logging
import threading
import json

try:
    # noinspection PyPep8Naming
    import ConfigParser as configparser
except ImportError:
    # noinspection PyUnresolvedReferences
    import configparser

import os
import requests
from requests.adapters import HTTPAdapter
import warnings
from missinglink.core.exceptions import NonRetryException


warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")


class GooglePackagesMissing(NonRetryException):
    pass


class GoogleAuthError(NonRetryException):
    pass


class GaeCredentials(object):
    @classmethod
    def get_project_id_from_gae(cls):
        from google.auth import app_engine

        try:
            return app_engine.get_project_id()
        except EnvironmentError:
            return None

    @classmethod
    def get_gae_credentials(cls, scopes, **kwargs):
        def _get_gae_credentials():
            logging.debug('_get_gae_credential')

            from google.auth import app_engine

            try:
                service_account_id = kwargs.pop('service_account_id', None)
                gae_credentials = app_engine.Credentials(scopes=scopes, service_account_id=service_account_id)
                return gae_credentials
            except EnvironmentError:
                return None

        return _get_gae_credentials


class GoogleCredentialsFile(object):
    CLOUD_SDK_CONFIG_DIR = 'CLOUDSDK_CONFIG'
    _CONFIG_DIRECTORY = 'gcloud'
    _CREDENTIALS_FILENAME = 'application_default_credentials.json'
    _WINDOWS_CONFIG_ROOT_ENV_VAR = 'APPDATA'
    _AUTHORIZED_USER_TYPE = 'authorized_user'
    _SERVICE_ACCOUNT_TYPE = 'service_account'
    _DEFAULT_CONFIG_FILE = 'config_default'
    _DEFAULT_CONFIG_PATH = 'configurations'
    _VALID_TYPES = (_AUTHORIZED_USER_TYPE, _SERVICE_ACCOUNT_TYPE)

    _file_cached_credentials_lock = threading.Lock()
    _file_cached_credentials = {}

    @classmethod
    def _get_auth_config_from_default_file(cls, filename):
        try:
            with open(filename) as file_obj:
                return json.load(file_obj)
        except (IOError, OSError) as ex:
            logging.debug('auth config file %s not found (%s)', filename, ex)
            return None

    @classmethod
    def get_config_path(cls):
        # If the path is explicitly set, return that.
        try:
            return os.environ[cls.CLOUD_SDK_CONFIG_DIR]
        except KeyError:
            pass

        # Non-windows systems store this at ~/.config/gcloud
        if os.name != 'nt':
            return os.path.join(os.path.expanduser('~'), '.config', cls._CONFIG_DIRECTORY)
        # Windows systems store config at %APPDATA%\gcloud
        else:
            try:
                return os.path.join(os.environ[cls._WINDOWS_CONFIG_ROOT_ENV_VAR], cls._CONFIG_DIRECTORY)
            except KeyError:
                # This should never happen unless someone is really
                # messing with things, but we'll cover the case anyway.
                drive = os.environ.get('SystemDrive', 'C:')
                return os.path.join(drive, '\\', cls._CONFIG_DIRECTORY)

    @classmethod
    def get_application_default_credentials_path(cls):
        config_path = cls.get_config_path()
        return os.path.join(config_path, cls._CREDENTIALS_FILENAME)

    @classmethod
    def _get_cached_credentials(cls, cache_key):
        with cls._file_cached_credentials_lock:
            return cls._file_cached_credentials.get(cache_key)

    @classmethod
    def _set_cached_credentials(cls, cache_key, credentials):
        with cls._file_cached_credentials_lock:
            cls._file_cached_credentials[cache_key] = credentials

    @classmethod
    def _service_account_load_redentials(cls, info, scopes, filename, **kwargs):
        try:
            from google.oauth2 import service_account
        except ImportError:
            raise GooglePackagesMissing()

        return service_account.Credentials.from_service_account_info(info, scopes=scopes, **kwargs)

    @classmethod
    def _authorized_user_load_redentials(cls, info, scopes, filename, **kwargs):
        try:
            from google.oauth2 import credentials as google_credentials
        except ImportError:
            raise GooglePackagesMissing()

        return google_credentials.Credentials.from_authorized_user_info(info, scopes=scopes)

    @classmethod
    def _not_supported_load_redentials(cls, info, scopes, filename, **kwargs):
        try:
            import google.auth.exceptions
        except ImportError:
            raise GooglePackagesMissing()

        credential_type = info.get('type')

        # noinspection PyUnresolvedReferences
        raise google.auth.exceptions.DefaultCredentialsError(
            'The file {file} does not have a valid type. '
            'Type is {type}, expected one of {valid_types}.'.format(
                file=filename, type=credential_type, valid_types=cls._VALID_TYPES))

    @classmethod
    def get_credentials_from_files(cls, scopes, **kwargs):
        def _cache_key(filename):
            return '{filename}{scopes}{kwargs}'.format(filename=filename, scopes=scopes, kwargs=kwargs)

        def _get_credentials_from_files():
            logging.debug('_get_credentials_from_files')

            filename = cls.get_application_default_credentials_path()

            cache_key = _cache_key(filename)
            cached_credentials = cls._get_cached_credentials(cache_key)

            if cached_credentials is not None:
                return cached_credentials

            info = cls._get_auth_config_from_default_file(filename)

            if info is None:
                return None

            credential_type = info.get('type')

            loader_method_name = '_%s_load_redentials' % credential_type

            loader_method = getattr(cls, loader_method_name, cls._not_supported_load_redentials)

            file_credentials = loader_method(info, scopes, filename, **kwargs)

            cls._set_cached_credentials(cache_key, file_credentials)

            return file_credentials

        return _get_credentials_from_files

    @classmethod
    def get_default_config_path(cls):
        config_path = cls.get_config_path()
        return os.path.join(config_path, cls._DEFAULT_CONFIG_PATH, cls._DEFAULT_CONFIG_FILE)

    @classmethod
    def _clear_files_cache(cls):
        with cls._file_cached_credentials_lock:
            cls._file_cached_credentials = {}

    @classmethod
    def get_project_id_from_path(cls):
        default_config = cls.get_default_config_path()
        config = configparser.ConfigParser()
        config.read(default_config)
        try:
            return config.get('core', 'project')
        except (configparser.NoOptionError, configparser.NoSectionError):
            return None


class GCPServices(object):
    def __init__(self):
        pass

    @classmethod
    def _setup_session(cls, session):
        a = HTTPAdapter(pool_maxsize=50)
        b = HTTPAdapter(pool_maxsize=50)
        session.mount('http://', a)
        session.mount('https://', b)

    @classmethod
    def get_default_project_id(cls):
        for project_id_method in (GaeCredentials.get_project_id_from_gae, GoogleCredentialsFile.get_project_id_from_path):
            project_id = project_id_method()
            if project_id is None:
                continue

            return project_id

    @classmethod
    def _get_gcloud_auth_session(cls, credentials):
        try:
            import google.auth.transport.requests
        except ImportError:
            raise GooglePackagesMissing()

        # noinspection PyUnresolvedReferences
        auth_method_session = google.auth.transport.requests.AuthorizedSession(credentials)
        cls._setup_session(auth_method_session)

        return auth_method_session

    @classmethod
    def gcp_default_credentials(cls, scopes=None, **kwargs):
        logging.debug('gcp_default_credentials %s %s', scopes, kwargs)

        method_checkers = [
            GaeCredentials.get_gae_credentials(scopes, **kwargs),
            GoogleCredentialsFile.get_credentials_from_files(scopes, **kwargs)
        ]

        for credentials_method in method_checkers:
            credentials = credentials_method()

            if credentials is None:
                continue

            return credentials

    @classmethod
    def gcs_service(cls, credentials):
        try:
            from google.cloud import storage
        except ImportError:
            raise GooglePackagesMissing()

        auth_method_session = cls._get_gcloud_auth_session(credentials)

        params = {'_http': auth_method_session, 'credentials': credentials}

        project = cls.get_default_project_id()
        if project is not None:
            params['project'] = project

        return storage.Client(**params)
