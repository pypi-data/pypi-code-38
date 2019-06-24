import base64
import json
import requests
import logging
import re
import pytz
import sys
import click
import http.client

from datetime import datetime
from pytz import timezone

from botocore import exceptions as boto_exceptions
from warrant import Cognito
from urllib.parse import urljoin

from cotoba_cli import config
from cotoba_cli import cognito

logger = logging.getLogger(__name__)

BOT_API_PATH = 'bots/'


class SignUpEmailExistsException(Exception):
    def __init__(self, email):
        self.email = email
        super().__init__('Email({}) already exists.'.format(self.email))


class SignUpPasswordInvalidException(Exception):
    def __init__(self):
        super().__init__('Password is invalid.')


class LoginEmailNotFoundException(Exception):
    def __init__(self, email):
        self.email = email
        super().__init__(
            'Account with email address({}) is not found.'.format(email))


class PlatformResponse:
    def __init__(self,
                 response_body_json,
                 http_status_code,
                 message_text,
                 request_body=None):
        self.__response_body_json = response_body_json
        self.__http_status_code = http_status_code
        self.__message_text = message_text
        self.__request_body = request_body

    def get_response_body(self):
        return json.loads(self.__response_body_json)

    def set_message(self, message):
        self.__message_text = message

    def print_message(self):
        if self.__message_text:
            click.echo(self.__message_text)

    def print(self, print_status=True):
        if print_status:
            if 400 <= self.__http_status_code:
                color = 'red'
            else:
                color = 'green'
            status_msg = http.client.responses[self.__http_status_code]
            status_text = str(self.__http_status_code) + ' ' + status_msg
            click.echo(click.style(
                status_text,
                fg=color),
                err=True
            )
        self.print_message()

    def get_request_time(self):
        return self.__request_body.get('time')


def sign_up(email, password, authorization=None):
    if not authorization:
        authorization = config.load()['default'].get('authorization')
        if not authorization:
            sys.stderr.write('Set authorization Id.\n')
            sys.exit(1)
    pool_id, client_id = decode_cognito_setting(authorization)

    cognito_user = Cognito(
        pool_id, client_id, username=email,
        access_key=cognito.ACCESS_KEY, secret_key=cognito.SECRET_KEY,
        user_pool_region=cognito.USER_POOL_REGION)
    cognito_user.add_base_attributes(email=email)
    try:
        cognito_user.register(email, password)
    except boto_exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'UsernameExistsException':
            e = SignUpEmailExistsException(email)
            sys.stderr.write(str(e) + '\n')
            sys.exit(1)
        else:
            sys.stderr.write('Unexpected error: {}\n'.format(e))
            sys.exit(1)
    except boto_exceptions.ParamValidationError as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    return cognito_user


def login(email, password, authorization=None):
    if not authorization:
        authorization = config.load()['default'].get('authorization')
        if not authorization:
            sys.stderr.write('Set authorization Id.\n')
            sys.exit(1)
    pool_id, client_id = decode_cognito_setting(authorization)

    cognito_user = Cognito(
        pool_id, client_id, username=email,
        access_key=cognito.ACCESS_KEY, secret_key=cognito.SECRET_KEY,
        user_pool_region=cognito.USER_POOL_REGION)
    try:
        cognito_user.authenticate(password=password)
    except boto_exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'UserNotFoundException':
            e = LoginEmailNotFoundException(email)
            sys.stderr.write(str(e) + '\n')
            sys.exit(1)
        else:
            sys.stderr.write('unexpected error.\n')
            sys.exit(1)
    return cognito_user


def create_bot(cognito_user, filepath, endpoint_url,
               message=None, nlu_url=None):
    with open(filepath, 'rb') as f:
        encoded_file = base64.b64encode(f.read()).decode('utf-8')
    headers = {
        'Authorization': cognito_user.id_token,
        'Content-Type': 'application/json; charset=utf-8'
    }
    body = {
        'file': encoded_file,
        'message': message,
        'nluUrl': nlu_url
        }
    body = {k: v for k, v in body.items() if v is not None}
    try:
        r = requests.post(
            urljoin(endpoint_url, BOT_API_PATH),
            json.dumps(body),
            headers=headers)
    except requests.RequestException as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    return PlatformResponse(r.text, r.status_code, r.text)


def update_bot(cognito_user, bot_id, endpoint_url, filepath=None,
               message=None, nlu_url=None):
    headers = {
        'Authorization': cognito_user.id_token,
        'Content-Type': 'application/json; charset=utf-8'
    }

    body = {
        'message': message,
        'nluUrl': nlu_url
    }

    if filepath:
        with open(filepath, 'rb') as f:
            body['file'] = base64.b64encode(
                f.read()).decode('utf-8')

    body = {k: v for k, v in body.items() if v is not None}

    try:
        r = requests.put(
            urljoin(endpoint_url, BOT_API_PATH + bot_id),
            json.dumps(body),
            headers=headers)
    except requests.RequestException as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    return PlatformResponse(r.text, r.status_code, r.text)


def list_bots(cognito_user, endpoint_url):
    headers = {
        'Authorization': cognito_user.id_token
    }
    try:
        r = requests.get(
            urljoin(endpoint_url, BOT_API_PATH),
            headers=headers)
    except requests.RequestException as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    return PlatformResponse(r.text, r.status_code, r.text)


def get_bot(cognito_user, bot_id, zipfile_path, endpoint_url):
    headers = {
        'Authorization': cognito_user.id_token
    }
    api_path = urljoin(endpoint_url, BOT_API_PATH + bot_id)
    if zipfile_path:
        api_path = api_path + '?include_scenario=true'
    try:
        r = requests.get(api_path, headers=headers)
        res = PlatformResponse(r.text, r.status_code, r.text)
    except requests.RequestException as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    if zipfile_path:
        with open(zipfile_path, 'wb') as f:
            f.write(base64.b64decode(res.get_response_body()['file']))
    return res


def delete_bot(cognito_user, bot_id, endpoint_url):
    headers = {
        'Authorization': cognito_user.id_token
    }
    try:
        r = requests.delete(
            urljoin(endpoint_url,  BOT_API_PATH + bot_id),
            headers=headers)
    except requests.RequestException as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    return PlatformResponse(r.text, r.status_code, r.text)


def ask_bot(
        bot_id,
        user_id,
        utterance,
        topic=None,
        metadata=None,
        log_level=None,
        locale=None,
        endpoint_url=None
):
    """
    Returns:
      (decode_response_text, unicode_response_text, request_time)
    """
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
        # TODO: use x-api-key to authenticate.
        # 'x-api-key': api_key
    }
    request_time = get_local_time(locale)
    payload = {
        "locale": locale,
        "time": request_time,
        "userId": user_id,
        "utterance": utterance,
    }
    if log_level is not None:
        payload['config'] = {"logLevel": log_level}
    if topic is not None:
        payload['topic'] = topic
    if metadata is not None:
        payload['metadata'] = metadata
    try:
        r = requests.post(
            urljoin(endpoint_url, BOT_API_PATH + bot_id + '/ask'),
            data=json.dumps(payload),
            headers=headers
        )
    except requests.RequestException as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    return PlatformResponse(r.text, r.status_code, r.text, payload)


def debug_bot(cognito_user, bot_id, endpoint_url, user_id=None):
    headers = {
        'Authorization': cognito_user.id_token
    }

    if user_id is None:
        user_id = "None"

    try:
        r = requests.post(
            urljoin(endpoint_url,  BOT_API_PATH + bot_id + '/debug'),
            json.dumps({
                'userId': user_id
            }),
            headers=headers)
    except requests.RequestException as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    return PlatformResponse(r.text, r.status_code, r.text)


def run_bot(cognito_user, bot_id, endpoint_url):
    headers = {
        'Authorization': cognito_user.id_token
    }
    try:
        r = requests.post(
            urljoin(endpoint_url, BOT_API_PATH + bot_id + '/run'),
            headers=headers)
    except requests.RequestException as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    return PlatformResponse(r.text, r.status_code, r.text)


def stop_bot(cognito_user, bot_id, endpoint_url):
    headers = {
        'Authorization': cognito_user.id_token
    }
    try:
        r = requests.post(
            urljoin(endpoint_url, BOT_API_PATH + bot_id + '/stop'),
            headers=headers)
    except requests.RequestException as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    return PlatformResponse(r.text, r.status_code, r.text)


def encode_cognito_setting(pool_id, client):
    connected_text = ','.join([pool_id, client])
    encoded_text = base64.encodebytes(connected_text.encode('ascii'))
    return encoded_text


def decode_cognito_setting(encoded_cognito_setting):
    """
    Returns:
      (pool_id, client_id)
    """
    if type(encoded_cognito_setting) is str:
        encoded_cognito_setting = encoded_cognito_setting.encode('ascii')
    try:
        decoded_text = base64.decodebytes(
            encoded_cognito_setting).decode('ascii')
    except base64.binascii.Error as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    if decoded_text.count(',') != 1:
        sys.stderr.write('Authorization Id is invalid.\n')
        sys.exit(1)
    return tuple(decoded_text.strip().split(','))


def get_local_time(locale):
    result = re.match('(?P<lang>.*)[_|-](?P<code>.*)', locale)
    country_code = result.group('code')
    tz_dict = pytz.country_timezones
    tz = tz_dict.get(country_code)
    return datetime.now(timezone(tz[0])).isoformat(timespec='seconds')


def get_conversations_history(cognito_user,
                              bot_id,
                              user_id,
                              history_size=None,
                              endpoint_url=None):
    debug_api_response = debug_bot(cognito_user,
                                   bot_id=bot_id,
                                   user_id=user_id,
                                   endpoint_url=endpoint_url)
    response_json = debug_api_response.get_response_body()
    conversations = response_json.get('conversations')
    if conversations is None:
        return []
    questions = conversations.get('questions')
    sentences = [x['sentences'] for x in questions]
    histories = [(x['question'], x['response']) for y in sentences for x in y]
    if history_size:
        # Get the specified number of elements from the end.
        histories = histories[-history_size:]
    histories.reverse()
    return histories


def show_talk_mode_description():
    click.secho('Start talk mode. '
                'If you enter "exit", exit talk mode.',
                fg='bright_cyan')
    echo_description('--topic',
                     'Topic ID.(e.g.:hello --topic greeting)')
    echo_description('--show-topic',
                     'Show response "topic".')
    echo_description('--show-metadata',
                     'Show response "metadata".')
    echo_description('--history-in',
                     'Show your input history. '
                     'By set parameter, specify number.')
    echo_description('--history-out',
                     'Show API response history. '
                     'By set parameter, specify number.')
    echo_description('--history',
                     'Show your input and API response history.')


def echo_description(command, help_text, columns=23):
    description = f'{command:<{columns}}' + help_text
    click.secho(description, fg='bright_cyan')
