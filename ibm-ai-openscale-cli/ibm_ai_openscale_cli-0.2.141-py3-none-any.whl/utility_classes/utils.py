# coding=utf-8
from __future__ import print_function

from requests.auth import HTTPBasicAuth
import json
import subprocess
import requests
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
import random

logger = FastpathLogger(__name__)

def executeCommandWithResult(cmd):
    '''
    Run command and capture the output of the command
    '''
    status, result = subprocess.getstatusoutput(cmd)
    if status != 0:
        return None
    return result


def executeCommand(cmd):
    '''
    Run command
    '''
    status, result = subprocess.getstatusoutput(cmd)
    if status != 0:
        error_msg = 'Exited with {} status while trying to execute {}. Reason: {}'.format(status, cmd, result)
        logger.log_error(error_msg)
        raise Exception(error_msg)


def jsonFileToDict(filename):
    '''
    reads the json file specfied and returns it as a dictionary
    '''
    result = None
    if (filename is not None and filename.strip()):
        with open(filename.strip()) as f:
            result = json.load(f)
    if result is None:
        error_msg = 'Unable to read file "{}"'.format(filename)
        logger.log_error(error_msg)
        raise Exception(error_msg)
    return result

def get_iam_headers(aios_credentials, env, auth_iam_token=None):
    # get a bearer token for storing historical measurementfacts
    iam_token = None
    if auth_iam_token:
        iam_token = auth_iam_token
    else:
        if env['name'].lower() == 'icp':
            response = requests.get(
                u'{}/v1/preauth/validateAuth'.format(aios_credentials['url']),
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                },
                auth=HTTPBasicAuth(aios_credentials['username'], aios_credentials['password']),
                verify=False
            )
            iam_token = response.json()['accessToken']
        else:
            token_data = {
                'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
                'response_type': 'cloud_iam',
                'apikey': aios_credentials['apikey']
            }
            response = requests.post(env['iam_url'], data=token_data)
            iam_token = response.json()['access_token']
    iam_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(iam_token)
    }
    return iam_headers

def get_error_message(response):
    """
    Gets the error message from a JSON response.
    :return: the error message
    :rtype: string
    """
    error_message = 'Unknown error'
    try:
        error_json = response.json()
        if 'error' in error_json:
            if isinstance(error_json['error'], dict) and 'description' in \
                    error_json['error']:
                error_message = error_json['error']['description']
            else:
                error_message = error_json['error']
        elif 'error_message' in error_json:
            error_message = error_json['error_message']
        elif 'message' in error_json:
            error_message = error_json['message']
        elif 'description' in error_json:
            error_message = error_json['description']
        elif 'errorMessage' in error_json:
            error_message = error_json['errorMessage']
        elif 'msg' in error_json:
            error_message = error_json['msg']
        return error_message
    except:
        return response.text or error_message

# random.choices() not available before Python 3.6
# expects a [] list of the choices and an equal-length [] list of integer weights
def choices(population, weights):
    sum_weights = 0
    for i in weights:
        sum_weights += i
    r = random.randint(0, sum_weights)
    choice = population[0]
    sum_weights = 0
    for i in range(len(weights)):
        sum_weights += weights[i]
        if r <= sum_weights:
            choice = population[i]
            break
    return choice
