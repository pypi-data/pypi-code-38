# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from __future__ import print_function
import pkg_resources
import re
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from ibm_ai_openscale.utils.client_errors import *
import json
import base64
from datetime import datetime, timedelta


PAYLOAD_LOGGING_DETAILS_TYPE = u'payload_logging_type'
FUNCTION_DETAILS_TYPE = u'function_details_type'

UNKNOWN_ARRAY_TYPE = u'resource_type'
UNKNOWN_TYPE = u'unknown_type'

requests_session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
requests_session.mount('http://', adapter)
requests_session.mount('https://', adapter)


def is_ipython():
    # checks if the code is run in the notebook
    try:
        get_ipython
        return True
    except Exception:
        return False


def get_type_of_details(details):
    if 'resources' in details:
        return UNKNOWN_ARRAY_TYPE
    elif details is None:
        raise ClientError('Details doesn\'t exist.')
    else:
        try:
            if re.search(u'\/functions\/[^\/]+$', details[u'metadata'][u'url']) is not None:
                return FUNCTION_DETAILS_TYPE
        except:
            pass

        try:
            if re.search(u'\/payload_logging\/[^\/]+$', details[u'metadata'][u'url']) is not None:
                return PAYLOAD_LOGGING_DETAILS_TYPE
        except:
            pass

        return UNKNOWN_TYPE


def docstring_parameter(args):
    def dec(obj):
        #obj.__doc__ = obj.__doc__.format(**args)
        return obj
    return dec


def version():
    try:
        version = pkg_resources.get_distribution("ibm-ai-openscale").version
    except pkg_resources.DistributionNotFound:
        version = u'0.0.1-local'

    return version


def install_package(package, version=None):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import subprocess

        if version is None:
            package_name = package
        else:
            package_name = "{}=={}".format(package, version)

        subprocess.call([sys.executable, '-m', 'pip', 'install', package_name])


def install_package_from_pypi(name, version=None, test_pypi=False):
    from setuptools.command import easy_install

    if version is None:
        package_name = name
    else:
        package_name = "{}=={}".format(name, version)

    if test_pypi:
        index_part = ["--index-url", "https://test.pypi.org/simple/"]
    else:
        index_part = ["--index-url", "https://pypi.python.org/simple/"]

    easy_install.main(index_part + [package_name])

    import importlib
    globals()[name] = importlib.import_module(name)


def handle_credentials(response):
    credential_keys = ['database_configuration']

    if type(response) is str:
        response = json.loads(response)

    if type(response) is dict:
        for key in credential_keys:
            if key in response.keys():
                response[key] = {}

    return response


def handle_response(expected_status_code, operationName, response, json_response=True):
    logger = logging.getLogger('handle_response')
    if response.status_code == expected_status_code:
        logger.info(u'Successfully finished {} for url: \'{}\''.format(operationName, response.url))
        logger.debug(u'Response({} {}): {}'.format(response.request.method, response.url, response.text))
        if json_response:
            try:
                return response.json()
            except Exception as e:
                raise ClientError(u'Failure during parsing json response: \'{}\''.format(response.text), e)
        else:
            return response.text
    elif response.status_code == 409:
        raise ApiRequestWarning(u'Warning during {}.'.format(operationName), response)
    else:
        raise ApiRequestFailure(u'Failure during {}.'.format(operationName), response)


def validate_enum(el, el_name, enum_class, mandatory=True):
    if mandatory and el is None:
        raise MissingValue(el_name)
    elif el is None:
        return

    validate_type(el, el_name, str, mandatory)

    acceptable_values = list(map(lambda y: enum_class.__dict__[y], list(filter(lambda x: not x.startswith('_'), enum_class.__dict__))))

    if el is not None and el not in acceptable_values:
        raise ClientError('Unexpected value of \'{}\', expected one of: {}, actual: {}'.format(el_name, acceptable_values, el))


def validate_type(el, el_name, expected_type, mandatory=True, subclass=False):
    if el_name is None:
        raise MissingValue(u'el_name')

    if type(el_name) is not str:
        raise UnexpectedType(u'el_name', str, type(el_name))

    if expected_type is None:
        raise MissingValue(u'expected_type')

    if type(expected_type) is not type and type(expected_type) is not list:
        raise UnexpectedType('expected_type', 'type or list', type(expected_type))

    if type(mandatory) is not bool:
        raise UnexpectedType(u'mandatory', bool, type(mandatory))

    if type(subclass) is not bool:
        raise UnexpectedType(u'subclass', bool, type(subclass))

    if mandatory and el is None:
        raise MissingValue(el_name)
    elif el is None:
        return

    validation_func = isinstance

    if subclass is True:
        validation_func = lambda x, y: issubclass(x.__class__, y)

    if type(expected_type) is list:
        try:
            next((x for x in expected_type if validation_func(el, x)))
            return True
        except StopIteration:
            return False
    else:
        if not validation_func(el, expected_type):
            raise UnexpectedType(el_name, expected_type, type(el))


def validate_meta_prop(meta_props, name, expected_type, mandatory=True):
    if name in meta_props:
        validate_type(meta_props[name], u'meta_props.' + name, expected_type, mandatory)
    else:
        if mandatory:
            raise MissingMetaProp(name)


def print_text_header_h1(title):
    print(u'\n\n' + (u'=' * (len(title) + 2)) + u'\n')
    print(' ' + title + ' ')
    print(u'\n' + (u'=' * (len(title) + 2)) + u'\n\n')


def print_text_header_h2(title):
    print(u'\n\n' + (u'-' * (len(title) + 2)))
    print(' ' + title + ' ')
    print((u'-' * (len(title) + 2)) + u'\n\n')


def print_synchronous_run(title, check_state, run_states=None, success_states=['success', 'finished'], failure_states=['failure', 'error', 'cancelled', 'canceled'], delay=5, get_result=None):
    if get_result is None:
        def tmp_get_result():
            if state in success_states:
                return 'Successfully finished.', None, None
            else:
                return 'Error occured.', None, None
        get_result = tmp_get_result

    print_text_header_h1(title)
    state = None

    start_time = time.time()
    elapsed_time = 0
    timeout = 180
    while (run_states is not None and state in run_states) or (state not in success_states and state not in failure_states):
        last_state = state
        state = check_state()

        if state != last_state:
            print('\n' + state, end='')
        else:
            print('.', end='')

        time.sleep(delay)
        elapsed_time = time.time() - start_time

        if elapsed_time > timeout:
            break

    if elapsed_time > timeout:
        result_title, msg, result = 'Run timed out', 'The run didn\'t finished within {}s.'.format(timeout), None
    else:
        result_title, msg, result = get_result()

    print_text_header_h2(result_title)
    if msg is not None:
        print(msg)

    return result


def decode_hdf5(encoded_val):
    import uuid
    import os
    import h5py

    filename = 'tmp_payload_' + str(uuid.uuid4()) + '.hdf5'

    try:
        with open(filename, 'wb') as f:
            f.write(base64.decodebytes(bytes(encoded_val, 'utf-8')))

        with h5py.File(filename, 'r') as content:
            return content['data'].value.tolist()
    finally:
        try:
            os.remove(filename)
        except:
            pass


def create_postgres_schema(postgres_credentials, schema_name):
    initial_level = logging.getLogger().getEffectiveLevel()
    install_package("psycopg2<2.8")
    updated_level = logging.getLogger().getEffectiveLevel()

    if initial_level != updated_level:
        logging.basicConfig(level=initial_level)

    import psycopg2

    conn_string = create_postgres_connection_string(postgres_credentials)
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    cursor = conn.cursor()
    try:
        query = "drop schema " + schema_name + " cascade"
        cursor.execute(query)
    except:
        pass
    finally:
        try:
            query = "create schema " + schema_name
            cursor.execute(query)
        finally:
            conn.close()


def create_postgres_connection_string(credentials):
    try:
        if 'uri' in credentials:
            hostname = credentials['uri'].split('@')[1].split(':')[0]
            port = credentials['uri'].split('@')[1].split(':')[1].split('/')[0]
            db_name = 'compose'
            user = credentials['uri'].split('@')[0].split('//')[1].split(':')[0]
            password = credentials['uri'].split('@')[0].split('//')[1].split(':')[1]
        elif 'connection' in credentials: #  Compose for PostgreSQL

            hostname = credentials['connection']['postgres']['hosts'][0]['hostname']
            port = credentials['connection']['postgres']['hosts'][0]['port']
            db_name = credentials['connection']['postgres']['database']
            user = credentials['connection']['postgres']['authentication']['username']
            password = credentials['connection']['postgres']['authentication']['password']
        else:
            raise ClientError('Not supported postgres credentials format.')

        return "host={} port={} dbname={} user={} password={}".format(hostname, port, db_name, user, password)
    except:
        raise ClientError('Not supported postgres credentials format.')


def validate_asset_properties(asset_properties, properties_list):
    keys = asset_properties.keys()

    for prop in properties_list:

        # TODO remove hooks for duplicated fields or different names when API is cleaned up
        if type(prop) is list:
            if not any([True for item in prop if item in keys]):
                if 'predicted_target_field' in prop or 'prediction_field' in prop:
                    raise MissingValue('prediction_column',
                                   reason='Subscription is missing required asset property. Missing parameter can be specified using subscription.update() method.')
                elif 'class_probability_fields' in prop or 'prediction_probability_field' in prop:
                    raise MissingValue('class_probability_columns or probability_column',
                                       reason='Subscription is missing required asset property. Missing parameter can be specified using subscription.update() method.')
                else:
                    raise MissingValue(''.join(prop),
                                 reason='Subscription is missing one of listed asset properties. Missing parameter can be specified using subscription.update() method.')
        else:
            if prop not in keys:
                if prop == 'predicted_target_field' or prop == 'prediction_field':
                    raise MissingValue('prediction_column',
                                        reason='Subscription is missing required asset property. Missing parameter can be specified using subscription.update() method.')
                elif prop == 'feature_fields' or prop == 'categorical_fields':
                    raise MissingValue(prop.replace('fields', 'columns'),
                                       reason='Subscription is missing required asset property. Missing parameter can be specified using subscription.update() method.')
                elif prop == 'output_data_schema':
                    raise MissingValue(prop,
                                       reason='Payload should be logged first to have output_data_schema populated.')
                else:
                    raise MissingValue(prop,
                                       reason='Subscription is missing required asset property. Missing parameter can be specified using subscription.update() method.')
            elif prop == 'output_data_schema':
                output_data_schema = asset_properties['output_data_schema']

                if 'predicted_target_field' in keys and asset_properties['predicted_target_field'] not in str(output_data_schema):
                    raise MissingValue(prop,
                                       reason='Column `{}` cannot be found in output_data_schema. Check if this column name is valid. Make sure that payload has been logged to populate schema.'.format(asset_properties['predicted_target_field']))
                elif 'prediction_field' in keys and asset_properties['prediction_field'] not in str(output_data_schema):
                    raise MissingValue(prop,
                                       reason='Column `{}` cannot be found in output_data_schema. Check if this column name is valid. Make sure that payload has been logged to populate schema.'.format(asset_properties['prediction_field']))


def get_asset_property(subscription, asset_property):
    asset_properties = subscription.get_details()['entity']['asset_properties']

    if asset_property in asset_properties:
        return asset_properties[asset_property]
    else:
        return None


def get_instance_guid(api_key):
    import requests

    instance_guid = None
    token_data = {
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        'response_type': 'cloud_iam',
        'apikey': api_key
    }

    response = requests.post('https://iam.bluemix.net/identity/token', data=token_data)
    iam_token = response.json()['access_token']
    iam_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % iam_token
    }

    resources = json.loads(
        requests.get('https://resource-controller.cloud.ibm.com/v2/resource_instances', headers=iam_headers).text)[
        'resources']

    for resource in resources:
        if "aiopenscale" in resource['id'].lower():
            instance_guid = resource['guid']

    return instance_guid


def get_paged_resource(method_func, url, headers, limit, initial_result, validate, merge, get_number_of_elements, join_character='?', default_limit=1000):
    result = initial_result

    counter = 0
    elements_no = 0
    while True:
        response = method_func(
            url + "{}limit={}&offset={}".format(join_character, min(default_limit, limit - elements_no if limit is not None else default_limit), counter*default_limit),
            headers=headers
        )

        validate(response)
        result = merge(result, response)

        counter += 1
        elements_no += get_number_of_elements(response)

        if get_number_of_elements(response) < default_limit or (limit is not None and elements_no == limit):
            return result


def generate_historical_timestamps(end_date=None, days=7, size=7 * 24):
    """
     Generate historical timestamps with interval of one hour
    """

    timestamps = []

    if end_date is None:
        end_date = datetime.utcnow()

    current_date = end_date
    time_delta = timedelta(seconds=days * 24 * 3600 / size)
    for _ in range(size):
        timestamps.append(current_date.strftime('%Y-%m-%dT%H:%M:%SZ'))
        current_date -= time_delta
    timestamps.reverse()

    return timestamps

