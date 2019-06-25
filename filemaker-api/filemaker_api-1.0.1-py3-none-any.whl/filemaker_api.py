import argparse
import base64
import logging

import requests
from requests.exceptions import HTTPError

__version__ = "1.0.1"

# This section adds logging capabilities to this script.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - PID[%(process)d] - [%(levelname)s]: %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def get_parser():
    """
    This is the parser for the arguments coming from STDIN. It parses all the input.
    :return: parser
    """
    docstr = ("""Example:
                 python -m filemaker -u <username> -p <password> -s <server_IP_or_FQDN> -db <database> -l <layout>""")
    parser = argparse.ArgumentParser(prog="filemaker", description=docstr)
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('-u', '--username', type=str, help='Username to connect to the server.',
                        required=True)
    parser.add_argument('-p', '--password', type=str, help='Password of the username to get connected to the server.',
                        nargs='+', required=True)
    parser.add_argument('-s', '--server', type=str, help='IP address or FQDN of the server.', required=True)
    parser.add_argument('-db', '--database', type=str, help='Database where to perform some actions.', required=True)
    parser.add_argument('-l', '--layout', type=str, help='Layout chosen for performing some actions.', required=False)
    parser.add_argument('-r', '--recordID', type=str, help='Record ID to delete.', required=False)
    # TODO: check if this new file contains a json file.
    parser.add_argument('-n', '--new', type=argparse.FileType('r'), help='New record to create.', required=False)
    # TODO: check if this new file contains a json file.
    # TODO: create a sub-parser to group this option with the recordID.
    parser.add_argument('-e', '--edit', type=argparse.FileType('r'), help='Edit for record. It depends on -r option.',
                        required=False)

    return parser


def auth_post(username, password, server, database):
    '''
    This method performs the authentication request based on the username and password. It uses base64 Basic
    authentication.
    :param server: The IP address or the FQDN.
    :param username: Username allowed to connect to the db.
    :param password: Password of the username.
    :param database: Name of the database used to get the connection.
    :return: The response.
    '''
    url = 'https://' + server + '/fmi/data/v1/databases/' + database + '/sessions'
    auth_params = username + ':' + ''.join(password)
    response = ''
    try:
        # TODO: Revoke the InsecureRequestWarning by removing the verify=False option. This is only for testing.
        # The following is the way that I created. The next one is the method preferred.
        response = requests.post(url, headers={'Authorization': b'Basic ' + base64.b64encode(auth_params.encode()),
                                               'Content-type': 'application/json'})
        response.raise_for_status()
    except HTTPError as http_err:
        logger.error('There is an error while trying to connect to the server.')
        logger.error(f'HTTP error has occurred: {http_err}')  # This will only work on python >= 3.6
    except Exception as err:
        logger.exception(f'Unknown error/exception has occurred. Please check the parameters provided: {err}')
    else:
        logger.info('Connection successful!')
    return response.json()


def close_api(server, database, sessionToken):
    url = 'https://' + server + '/fmi/data/v1/databases/' + database + '/sessions/' + sessionToken
    response_close = ''
    try:
        response_close = requests.delete(url)
        response_close.raise_for_status()
    except HTTPError as http_err:
        logger.error('There is an error while trying to get disconnected.')
        logger.error(f'HTTP error has occurred: {http_err}')  # This will only work on python >= 3.6
    except Exception as err:
        logger.exception(f'Unknown error/exception has occurred. Please check the error: {err}')
    else:
        logger.info('Disconnection successful!')
    return response_close.json()


def create_record(server, database, sessionToken, layout, payload):
    url = 'https://' + server + '/fmi/data/v1/databases/' + database + '/layouts/' + layout + '/records'
    response = ''
    try:
        response = requests.post(url, headers={'Authorization': 'Bearer ' + sessionToken,
                                               'Content-type': 'application/json'}, json=payload)
        response.raise_for_status()
    except HTTPError as http_err:
        logger.error(f'HTTP error has occurred: {http_err}')  # This will only work on python >= 3.6
    except Exception as err:
        logger.exception(f'Unknown error/exception has occurred. Please check the error: {err}')
    else:
        logger.info('The record has been created successfully!')
    return response.json()


def delete_record(server, database, sessionToken, layout, recordID):
    url = 'https://' + server + '/fmi/data/v1/databases/' + database + '/layouts/' + layout + '/records/' + recordID
    response = ''
    try:
        response = requests.delete(url, headers={'Authorization': 'Bearer ' + sessionToken,
                                                 'Content-type': 'application/json'})
        response.raise_for_status()
    except HTTPError as http_err:
        logger.error(f'HTTP error has occurred: {http_err}')  # This will only work on python >= 3.6
    except Exception as err:
        logger.exception(f'Unknown error/exception has occurred. Please check the error: {err}')
    else:
        logger.info(f'The record {recordID} has been deleted successfully!')
    return response.json()


def get_record(server, database, sessionToken, layout, recordID):
    url = 'https://' + server + '/fmi/data/v1/databases/' + database + '/layouts/' + layout + '/records/' + recordID
    response = ''
    try:
        response = requests.get(url, headers={'Authorization': 'Bearer ' + sessionToken,
                                              'Content-type': 'application/json'})
        response.raise_for_status()
    except HTTPError as http_err:
        logger.error(f'HTTP error has occurred: {http_err}')  # This will only work on python >= 3.6
    except Exception as err:
        logger.exception(f'Unknown error/exception has occurred. Please check the error: {err}')
    else:
        logger.info(f'The record {recordID} has been obtained successfully!')
    return response.json()


def get_all_records(server, database, sessionToken, layout):
    url = 'https://' + server + '/fmi/data/v1/databases/' + database + '/layouts/' + layout + '/records'
    response = ''
    try:
        response = requests.get(url, headers={'Authorization': 'Bearer ' + sessionToken,
                                              'Content-type': 'application/json'})
        response.raise_for_status()
    except HTTPError as http_err:
        logger.error(f'HTTP error has occurred: {http_err}')  # This will only work on python >= 3.6
    except Exception as err:
        logger.exception(f'Unknown error/exception has occurred. Please check the error: {err}')
    else:
        logger.info('The records have been downloaded successfully!')
    return response.json()


def edit_record(server, database, sessionToken, layout, payload, recordID):
    url = 'https://' + server + '/fmi/data/v1/databases/' + database + '/layouts/' + layout + '/records/' + recordID
    response = ''
    try:
        response = requests.patch(url, headers={'Authorization': 'Bearer ' + sessionToken,
                                                'Content-type': 'application/json'}, json=payload)
        response.raise_for_status()
    except HTTPError as http_err:
        logger.error(f'HTTP error has occurred: {http_err}')  # This will only work on python >= 3.6
    except Exception as err:
        logger.exception(f'Unknown error/exception has occurred. Please check the error: {err}')
    else:
        logger.info('The record has been edited successfully!')
    return response.json()
