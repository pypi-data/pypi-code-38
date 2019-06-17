# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from contextlib import contextmanager
import datetime
import json
import logging
import os
import time

from azureml._base_sdk_common.process_utilities import start_background_process
from azureml._base_sdk_common.common import normalize_windows_paths
from azureml._base_sdk_common.service_discovery import get_service_url


VERSION = "v1"

HOME_AZUREML_PATH = os.path.join(os.path.expanduser('~'), ".azureml")
CLI_FLIGHT_CACHE = os.path.join(HOME_AZUREML_PATH, "cli-flights.json")
DEFAULT_FLIGHT_CONFIG = os.path.join(os.path.dirname(__file__), "default_config.json")
FLIGHT_MEMBERSHIP_URL = '/flighting/v1.0/full'
FLIGHT_MEMBERSHIP_URL_WITHOUT_ACCOUNT_SCOPE = FLIGHT_MEMBERSHIP_URL + '?subscriptionId={0}&emailAddress={1}'
FLIGHT_MEMBERSHIP_URL_WITH_ACCOUNT_SCOPE = FLIGHT_MEMBERSHIP_URL_WITHOUT_ACCOUNT_SCOPE + '&accountScope={2}'


class FlightCache():
    '''
    The FlightCache provides flight retrieval and caching functionality.
    If auto_refresh is set to True, the cache will update the entries automatically
    when queried through a background process. Otherwise, flight updates can be
    started by calling query_flighting_service.
    '''
    def __init__(self, auto_refresh=True, cache_file_location=CLI_FLIGHT_CACHE):
        self._auto_refresh = auto_refresh
        self._cache_file = os.path.abspath(cache_file_location)
        self._ensure_cache_exists()

    def get_default_configuration_value(self, key):
        '''
        Retrieves the default configuration value from the hard-coded default_config.json
        '''
        default_entry = self._read_cache(cache_file_name=DEFAULT_FLIGHT_CONFIG).get("default")
        if default_entry and 'configuration' in default_entry:
            return default_entry['configuration'].get(key)
        else:
            return None

    def get_configuration_value(self,
                                key,
                                subscription_id,
                                auth,
                                experimentation_scope=None,
                                wait=None):
        '''
        Get a configuration value for the provided information based on the configuration key

        :param subscription_id: the user's subscription
        :param auth: an instance of AzureCliAuthentication
        :param experimentation_scope: for whose flights to query, scope refers to
            /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/workspaces/<ws>
        '''
        configuration_values = self.get_all_configuration_values(subscription_id,
                                                                 auth,
                                                                 experimentation_scope,
                                                                 wait)

        if configuration_values:
            return configuration_values.get(key)
        return None

    def get_all_configuration_values(self,
                                     subscription_id,
                                     auth,
                                     experimentation_scope=None,
                                     wait=None):
        '''
        Get all configuration values for the provided information

        :param subscription_id: the user's subscription
        :param auth: an instance of AzureCliAuthentication
        :param experimentation_scope: for whose flights to query, scope refers to
            /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/workspaces/<ws>
        '''
        flight_cache_entry = self._get_flight_cache_entry(subscription_id,
                                                          auth,
                                                          experimentation_scope,
                                                          wait)

        if flight_cache_entry:
            return flight_cache_entry.get('configuration')
        return None

    def get_flights(self, subscription_id, auth, experimentation_scope=None, wait=None):
        '''
        Get all flights for the provided information

        :param subscription_id: the user's subscription
        :param auth: an instance of AzureCliAuthentication
        :param experimentation_scope: for whose flights to query, scope refers to
            /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/workspaces/<ws>
        '''
        flight_cache_entry = self._get_flight_cache_entry(subscription_id,
                                                          auth,
                                                          experimentation_scope,
                                                          wait)

        if flight_cache_entry:
            return flight_cache_entry.get('flights')
        return None

    def query_flighting_service(self, service_url, subscription_id, email_address, experimentation_scope=None):
        '''
        Queries the flighting service for flights and corresponding configuration values
        based on the provided subscription, experimentation account ID, and
        the email address. The resulting flights and values are stored in a JSON file for now.

        :param subscription_id: the user's subscription
        :param experimentation_scope: for whose flights to query, scope refers to
            /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/workspaces/<ws>
        '''
        # query for flight membership based on account, subscription and email
        flights, configuration_dict = self._query_for_flights(service_url,
                                                              subscription_id,
                                                              email_address,
                                                              experimentation_scope)

        key = _get_key_from_email_address_and_arm_scope(email_address, experimentation_scope, subscription_id)
        self._write_to_cache(key, flights, configuration_dict)

    def query_flighting_service_for_default_set(self):
        '''
        Queries the flighting service for the default configuration values. The resulting values
        are stored in a JSON file under "default" for now.
        '''
        self._ensure_cache_exists()

        # query for configuration values, ignore flights

        _, configuration_dict = self._query_for_flights(_get_default_service_url())

        self._write_to_cache('default', [], configuration_dict, cache_file_name=DEFAULT_FLIGHT_CONFIG)

    def _query_for_flights(self,
                           service_url,
                           subscription_id=None,
                           email_address=None,
                           experimentation_scope=None):
        logger = logging.getLogger('azureml._flighting.flight_cache._query_for_flights')

        # query for flight membership based on account, subscription and email
        flight_membership_url = _get_flight_membership_url(subscription_id,
                                                           email_address,
                                                           experimentation_scope)
        headers = {'Content-Type': 'application/json'}
        logger.info('querying flighting service for flights: {0}{1}'.format(service_url, flight_membership_url))

        full_flight_information = _call_service(service_url + flight_membership_url, headers=headers).json()

        flights = full_flight_information['flights']
        logger.info('retrieved the following flights: {0}'.format(', '.join(flights)))

        configuration_dict = full_flight_information['configurationValues']
        logger.info('retrieved the following configuration values: {0}'
                    .format(', '.join(["{0}: {1}".format(key, value)
                                       for (key, value) in configuration_dict.items()])))

        return flights, configuration_dict

    def _ensure_cache_exists(self):
        if not os.path.exists(self._cache_file):
            self._create_initial_cache()
        else:
            if self._read_cache().get('version') != VERSION:
                self._create_initial_cache()

    def _create_initial_cache(self):
        if not os.path.exists(HOME_AZUREML_PATH):
            os.makedirs(HOME_AZUREML_PATH)
        with open(self._cache_file, 'w') as cache_file:
            with _lock_file(cache_file):
                # if lock cannot be acquired another process is creating the cache
                cache_file.write(json.dumps({'version': VERSION}))

    def _read_cache(self, cache_file_name=None):
        '''
        Reads and returns all the contents of the flight cache JSON file.
        '''
        if cache_file_name is None:
            cache_file_name = self._cache_file

        with open(cache_file_name, 'r') as cache_file:
            with _lock_file(cache_file):
                return json.load(cache_file)

            # only happens if lock cannot be acquired within 10 second timeout period
            # on Windows or immediately on Unix/Linux
            return {}

    def _get_flight_cache_entry(self, subscription_id, auth, experimentation_scope=None, wait=None):
        '''
        Retrieves the flight cache entry if it exists, otherwise retrieves it from the flighting service.
        The method only waits for the result if a wait period is specified, otherwise just returns the default
        configuration from default_config.json.
        From this entry, the caller can extract flights and configuration values.

        :param subscription_id: the user's subscription
        :param auth: an instance of AzureCliAuthentication
        :param experimentation_scope: for whose flights to query, ID refers to the scope which is
            /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/workspaces/<ws>
        :param wait: the default (None) indicates no waiting period,
            otherwise specify the number of seconds to wait for the result
        '''
        if wait is not None and type(wait) != int:
            wait = None

        email_address = "nobody@example.com"

        flight_cache_key = _get_key_from_email_address_and_arm_scope(email_address,
                                                                     experimentation_scope,
                                                                     subscription_id)
        flight_cache_json = self._read_cache()

        issue_query_to_flighting_service = False
        return_value = None

        if flight_cache_key in flight_cache_json:
            return_value = flight_cache_json[flight_cache_key]
            if 'lastUpdate' in return_value:
                last_update_time = datetime.datetime.strptime(return_value['lastUpdate'], '%Y-%m-%d %H:%M:%S.%f')
                if datetime.datetime.now() - last_update_time > datetime.timedelta(hours=1):
                    issue_query_to_flighting_service = True
            else:
                # missing lastUpdate - query again
                issue_query_to_flighting_service = True
        else:
            # flights have never been queried for this user
            issue_query_to_flighting_service = True

        if self._auto_refresh and issue_query_to_flighting_service:
            self._ensure_cache_exists()

            email_address = "nobody@example.com"

            # the service URL is required to query the flighting service
            if experimentation_scope is None:
                service_url = _get_default_service_url()
            else:
                service_url = get_service_url(auth, experimentation_scope, None)

            args = [service_url]
            args.append(subscription_id)
            args.append("nobody@example.com")
            if experimentation_scope is not None:
                args.append(experimentation_scope)
            process = self._create_subprocess_for_refresh('query_flighting_service', args)

            if return_value is None and wait is not None:
                # wait for the results until the wait period is over
                wait_start = datetime.datetime.now()
                while datetime.timedelta(seconds=wait) > datetime.datetime.now() - wait_start:
                    if process.poll() is not None:
                        break
                    # check every half second since the queries usually take between 1 and 2 seconds
                    time.sleep(0.5)

                # read cache again
                flight_cache_json = self._read_cache()
                if flight_cache_key in flight_cache_json:
                    return_value = flight_cache_json[flight_cache_key]

        # TODO: we don't currently get or update the default set since it's hard-coded
        #     self._create_subprocess_for_refresh('query_flighting_service_for_default_set', [])
        default_entry = self._read_cache(cache_file_name=DEFAULT_FLIGHT_CONFIG).get("default")
        if return_value is None:
            # read default set from JSON file
            return_value = default_entry
        else:
            # hard-coded default may have extra key-value pairs, add those
            for configuration_key, configuration_value in default_entry.get('configuration', []).items():
                if configuration_key not in return_value['configuration']:
                    return_value['configuration'][configuration_key] = configuration_value

        return return_value

    def _create_subprocess_for_refresh(self, method_name, parameter_list):
        import_command = 'from azureml._flighting.flight_cache import FlightCache'

        if len(parameter_list) == 0:
            refresh_parameters = ''
        else:
            refresh_parameters = '\'{0}\''.format('\', \''.join(parameter_list))

        cache_file = normalize_windows_paths(self._cache_file)

        constructor_args = 'auto_refresh={0}, cache_file_location=\'{1}\'' \
            .format(self._auto_refresh, cache_file)

        refresh_command = 'FlightCache({0}).{1}({2})' \
            .format(
                constructor_args,
                method_name,
                refresh_parameters)

        command = ["python", "-c", "{0}; {1}".format(import_command, refresh_command)]
        return start_background_process(command)

    def _write_to_cache(self, key, flights, configuration_dict, cache_file_name=None):
        '''
        Writes the flights and configuration key-value pairs to the cache.

        :param flights: overwrites the existing cached flights with the flights list
        :param configuration_dict: overwrites the existing configuration with the passed dictionary
        '''
        self._ensure_cache_exists()

        flight_cache_json = self._read_cache()

        flight_cache_json[key] = {
            'flights': flights,
            'configuration': configuration_dict,
            'lastUpdate': str(datetime.datetime.now())}

        if cache_file_name is None:
            cache_file_name = self._cache_file

        with open(cache_file_name, 'w') as cache_file:
            with _lock_file(cache_file):
                # only write to file if lock was acquired
                cache_file.write(json.dumps(flight_cache_json))


def get_flight_cache():
    return FlightCache(auto_refresh=True, cache_file_location=CLI_FLIGHT_CACHE)


def _call_service(url, headers):
    import requests
    response = requests.get(url, headers=headers)
    if not response.ok:
        raise ConnectionError('Could not connect to the flighting service. HTTP Status Code {0}'
                              .format(response.status_code))
    return response


def _get_key_from_email_address_and_arm_scope(email_address, arm_scope, subscription_id):
    if arm_scope is None:
        return '{0}-/subscriptions/{1}'.format(email_address, subscription_id)
    return '{0}-{1}'.format(email_address, arm_scope)


def _get_default_service_url():
    return 'https://eastus2.experiments.azureml.net'


def _get_backup_service_url():
    # TODO: use backup if primary default service is not responding
    return 'https://westeurope.experiments.azureml.net'


def _get_flight_membership_url(subscription_id=None, email_address=None, experimentation_scope=None):
        if experimentation_scope:
            return FLIGHT_MEMBERSHIP_URL_WITH_ACCOUNT_SCOPE \
                .format(subscription_id, email_address, experimentation_scope)
        elif subscription_id and email_address:
            return FLIGHT_MEMBERSHIP_URL_WITHOUT_ACCOUNT_SCOPE \
                .format(subscription_id, email_address)
        else:
            return FLIGHT_MEMBERSHIP_URL


@contextmanager
def _lock_file(file):
    '''
    Lock file as long as it is opened. The caller has to ensure that the file is closed or unlock manually.
    Ideally, use this function with a pattern such as
    with open(file_name, 'a+') as file:
        with _lock_file(file):
            # do something
        else:
            # handle that we cannot lock the file

    :rtype: bool
    :return: True if locking was successful, otherwise False
    '''
    locked = False
    try:
        if os.name == "nt":
            # Windows specific locking
            import msvcrt
            # we have to lock at least 1 byte, but if the file does not exist yet the size is 0
            msvcrt.locking(file.fileno(), msvcrt.LK_RLCK, max([os.path.getsize(os.path.realpath(file.name)), 1]))
        else:
            # Posix based file locking (Linux, Ubuntu, MacOS, etc.)
            import fcntl
            fcntl.lockf(file, fcntl.LOCK_EX)
        locked = True
        yield locked
    except Exception:
        yield locked
    finally:
        try:
            # in Windows the file is automatically unlocked
            if locked and os.name != 'nt':
                import fcntl
                fcntl.lockf(file, fcntl.LOCK_UN)
        except Exception:
            pass
