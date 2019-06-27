import argparse
import logging

import requests
from requests.exceptions import HTTPError

__all__ = ['get_parser', 'create_export_response', 'get_export_responses_progress', 'get_export_file']
__version__ = "1.0.5"


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
                 python -m qualtrics-api -t <token_api> -o <organization_id> -d <datacenter_id> 
                 -s <survey_ID>""")
    parser = argparse.ArgumentParser(prog='qualtrics-api', description=docstr, epilog='Powered by W@xP!')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('-t', '--token', type=str, help='Token obtained from Qualtrics API.',
                        nargs='+', required=True)
    parser.add_argument('-o', '--organization', type=str, help='Organization.', required=False)
    parser.add_argument('-d', '--datacenter', type=str, help='Datacenter ID.', required=True)
    parser.add_argument('-s', '--survey', type=str, help='SurveyID to download.', required=False)
    return parser


def create_export_response(data_center_id, token, survey_id, format_out='json', questions=None,
                           start_date=None, end_date=None):
    url = 'https://' + data_center_id + '.qualtrics.com/API/v3/surveys/' + survey_id + '/export-responses/'
    response = ''
    payload = {"format": format_out, "compress": 'false'}
    if start_date and end_date:
        payload["startDate"] = start_date
        payload["endDate"] = end_date

    if questions:
        payload["questionIds"] = questions

    try:
        response = requests.post(url, headers={'X-API-TOKEN': ''.join(token),
                                               'Content-type': 'application/json'}, json=payload)
        response.raise_for_status()
    except HTTPError as http_err:
        logger.error(f'HTTP error has occurred: {http_err}')  # This will only work on python >= 3.6
    except Exception as err:
        logger.exception(f'Unknown error/exception has occurred. Please check the error: {err}')
    else:
        logger.info('The set of records have been requested successfully!')
    return response.json()


def get_export_responses_progress(data_center_id, token, survey_id, progress_id):
    url = 'https://' + data_center_id + '.qualtrics.com/API/v3/surveys/' + survey_id + '/export-responses/' \
          + progress_id
    response = None
    flag = True
    while flag or response is None:
        try:
            response = requests.get(url, headers={'X-API-TOKEN': ''.join(token),
                                                  'Content-type': 'application/json'})
            response.raise_for_status()
            progress = response.json()['result']['percentComplete']
            if response.json()['result']['percentComplete'] == 100.0:
                flag = False
        except HTTPError as http_err:
            logger.error(f'HTTP error has occurred: {http_err}')  # This will only work on python >= 3.6
        except Exception as err:
            logger.exception(f'Unknown error/exception has occurred. Please check the error: {err}')
        else:
            logger.info(f'The record progress is {progress}')
    return response.json()['result']['fileId']


def get_export_file(data_center_id, token, survey_id, file_id):
    url = 'https://' + data_center_id + '.qualtrics.com/API/v3/surveys/' + survey_id + '/export-responses/' + file_id \
          + '/file'
    response = None
    try:
        response = requests.get(url, headers={'X-API-TOKEN': ''.join(token),
                                              'Content-type': 'application/json'})
        response.raise_for_status()
    except HTTPError as http_err:
        logger.error(f'HTTP error has occurred: {http_err}')  # This will only work on python >= 3.6
    except Exception as err:
        logger.exception(f'Unknown error/exception has occurred. Please check the error: {err}')
    else:
        logger.info('The survey responses had been downloaded successfully!')
    return response.json()
