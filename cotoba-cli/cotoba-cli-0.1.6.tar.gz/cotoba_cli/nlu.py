import csv
import json
import requests
import os
import logging
import gzip
import mimetypes
import sys
from urllib.parse import urljoin
from cotoba_cli import platform

logger = logging.getLogger(__name__)


ENDPOINT_URL_MAP = {
    'algorithm': 'nlu/algorithm',
    'inferences': 'nlu/models',
    'model_metadata': 'nlu/models',
    'remaining_resources': 'nlu/remaining',
    'training_job': 'nlu/models',
    'training_data': 'nlu/data',
    'slot_dictionary': 'nlu/slotdict'
}

TRAINING_DATA_SIZE_LIMIT = 2 * 1024 * 1024
SLOT_DICTIONARY_SIZE_LIMIT = 100 * 1024 * 1024


def create_training_data(cognito_user, data_name, filepath,
                         description='None', limit=TRAINING_DATA_SIZE_LIMIT,
                         endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['training_data'])
    error_msg = check_training_data(filepath, limit)
    if error_msg is not None:
        sys.stderr.write(error_msg + '\n')
        sys.exit(1)

    headers = {
        'Authorization': cognito_user.access_token,
        'Content-Type': 'application/json'
    }
    r = requests.post(
        endpoint_url,
        json.dumps({
            'dataName': data_name,
            'description': description
        }),
        headers=headers)
    res = platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['message'])
    )
    r_json = res.get_response_body()
    if 'uploadUrl' in r_json:
        upload_url = r_json['uploadUrl']
        try:
            with open(filepath, 'rb') as f:
                requests.put(upload_url, data=f)
        except Exception as e:
            sys.stderr.write(str(e) + '\n')
            sys.exit(1)
        res.set_message({
            'message': 'File uploaded successfully.'
        })
    return res


def check_training_data(filepath, limit=TRAINING_DATA_SIZE_LIMIT):
    """
    訓練データのファイルフォーマットチェックを行う。
    Parameters
        filepath: str
            チェック対象のファイルパス
        limit: int
            ファイルの許容サイズ
    Returns
        チェックに失敗した時: エラーメッセージ
        問題ないとき: None
    """

    training_data = None
    mime = None
    try:
        if os.path.getsize(filepath) > limit:
            return 'File size limit exceeded for uploading.'
        mime = mimetypes.guess_type(filepath)
        if 'gzip' in mime:
            with gzip.open(filepath, 'r', 'utf-8') as f:
                training_data = json.load(f)
        elif 'application/json' in mime:
            with open(filepath) as f:
                training_data = json.load(f)
        else:
            return 'The file format must be "json" or "gzip".'
    except json.JSONDecodeError as e:
        return str(e)
    except FileNotFoundError as e:
        return str(e)

    if 'training' not in training_data:
        return 'The key "{}" is required for the file.'.format('training')

    valid_keys = ['training', 'validation']
    for key in training_data.keys():
        if key not in valid_keys:
            return 'The key of "{0}" is invalid. The key "{1}" is valid.' \
                .format(key, valid_keys)

        error_msg = 'Format error of data {0} of key "{1}": {2}'

        for line_number, data in enumerate(training_data[key]):

            if 'text' not in data:
                return error_msg.format(
                    line_number, key, 'There must be "text" in request.')
            if not isinstance(data['text'], str):
                return error_msg.format(
                    line_number, key,
                    'The type of "text" is invalid. The type "str" is valid.')

            if 'intent' not in data:
                return error_msg.format(
                    line_number, key, 'There must be "intent" in request.')
            if not isinstance(data['intent'], list):
                return error_msg.format(
                    line_number, key,
                    'The type of "intent" is invalid. '
                    'The type "[str]" is valid.')

            for intent in data['intent']:
                if not isinstance(intent, str):
                    return error_msg.format(
                        line_number, key,
                        'The type of "intent" is invalid. '
                        'The type "[str]" is valid.')

            if 'slot' not in data:
                return error_msg.format(
                    line_number, key, 'There must be "slot" in request.')
            if not isinstance(data['slot'], list):
                return error_msg.format(
                    line_number, key,
                    'The type of "slot" is invalid. '
                    'The type "list" is valid.')

            for slot in data['slot']:
                if 'type' not in slot:
                    return error_msg.format(
                        line_number, key,
                        'There must be "type" in request of "slot".')
                if not isinstance(slot['type'], str):
                    return error_msg.format(
                        line_number, key,
                        'The type of "type" is invalid. '
                        'The type "str" is valid.')
                if 'start' not in slot:
                    return error_msg.format(
                        line_number, key,
                        'There must be "start" in request of "slot".')
                if not isinstance(slot['start'], int):
                    return error_msg.format(
                        line_number, key,
                        'The type of "start" is invalid. '
                        'The type "int" is valid.')
                if 'end' not in slot:
                    return error_msg.format(
                        line_number, key,
                        'There must be "end" in request of "slot".')
                if not isinstance(slot['end'], int):
                    return error_msg.format(
                        line_number, key,
                        'The type of "end" is invalid. '
                        'The type "int" is valid.')
    return None


def update_training_data(cognito_user, training_data_id, description,
                         endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['training_data'])
    training_data_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, training_data_id)
    headers = {
        'Authorization': cognito_user.access_token,
        'Content-Type': 'application/json'
    }
    r = requests.put(
        '{}/{}'.format(endpoint_url, training_data_id),
        json.dumps({
            'description': description
        }),
        headers=headers)
    return platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['message'])
    )


def delete_training_data(cognito_user, training_data_id,
                         endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['training_data'])
    training_data_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, training_data_id)
    headers = {
        'Authorization': cognito_user.access_token,
    }
    r = requests.delete(
        '{}/{}'.format(endpoint_url, training_data_id),
        headers=headers)
    return platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['message'])
    )


def read_training_data(cognito_user, training_data_id,
                       endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['training_data'])
    training_data_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, training_data_id)
    headers = {
        'Authorization': cognito_user.access_token,
    }
    r = requests.get(
        '{}/{}'.format(endpoint_url, training_data_id),
        headers=headers)
    res = platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['dataId', 'message'])
    )
    return res


def list_training_data(cognito_user,
                       endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['training_data'])
    headers = {
        'Authorization': cognito_user.access_token,
    }
    r = requests.get(
        endpoint_url,
        headers=headers)
    res = platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['dataId'])
    )
    return res


def list_algorithm(endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['algorithm'])
    r = requests.get(
        endpoint_url)

    return platform.PlatformResponse(r.text, r.status_code, r.text)


def read_algorithm_hyper_parameter(image_name,
                                   endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['algorithm'])
    r = requests.get(
        '{}/{}/hyperparameters'.format(endpoint_url, image_name))
    return platform.PlatformResponse(r.text, r.status_code, r.text)


def create_slot_dictionary(cognito_user, data_name, filepath,
                           description='None',
                           limit=SLOT_DICTIONARY_SIZE_LIMIT,
                           endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['slot_dictionary'])
    error_msg = check_slot_dictionary(filepath, limit)
    if error_msg is not None:
        sys.stderr.write(error_msg + '\n')
        sys.exit(1)

    headers = {
        'Authorization': cognito_user.access_token,
        'Content-Type': 'application/json'
    }
    r = requests.post(
        endpoint_url,
        json.dumps({
            'dataName': data_name,
            'description': description
        }),
        headers=headers)
    res = platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['message'])
    )
    r_json = res.get_response_body()
    if 'uploadUrl' in r_json:
        upload_url = r_json['uploadUrl']
        try:
            with open(filepath, 'rb') as f:
                requests.put(upload_url, data=f)
        except Exception as e:
            sys.stderr.write(str(e) + '\n')
            sys.exit(1)
        res.set_message({
            'message': 'File uploaded successfully.'
        })
    return res


def check_slot_dictionary(filepath, limit=SLOT_DICTIONARY_SIZE_LIMIT):
    """
    slot辞書のファイルフォーマットチェックを行う。
    Parameters
        filepath: str
            チェック対象のファイルパス
        limit: int
            ファイルの許容サイズ
    Returns
        チェックに失敗した時: エラーメッセージ
        問題ないとき: None
    """

    try:
        if os.path.getsize(filepath) > limit:
            return 'File size limit exceeded for uploading.'
    except FileNotFoundError as e:
        return str(e)

    slot_dictionary_file = None
    try:
        mime = mimetypes.guess_type(filepath)
        if 'gzip' in mime:
            slot_dictionary_file = gzip.open(filepath, 'rt', 'utf-8')
        else:
            slot_dictionary_file = open(filepath, 'r', encoding='utf-8')
        slot_dictionary_csv = csv.reader(slot_dictionary_file, delimiter='\t')
        for line_number, line in enumerate(slot_dictionary_csv):
            if len(line) != 2:
                return 'Format error of line {}. 2 column "TSV" is valid.' \
                    .format(line_number)
    finally:
        slot_dictionary_file.close()

    return None


def read_slot_dictionary(cognito_user, slot_dictionary_id,
                         endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['slot_dictionary'])
    slot_dictionary_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, slot_dictionary_id)
    headers = {
        'Authorization': cognito_user.access_token,
    }
    r = requests.get(
        '{}/{}'.format(endpoint_url, slot_dictionary_id),
        headers=headers)

    res = platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['dataId', 'message'])
    )
    return res


def delete_slot_dictionary(cognito_user, slot_dictionary_id,
                           endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['slot_dictionary'])
    slot_dictionary_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, slot_dictionary_id)
    headers = {
        'Authorization': cognito_user.access_token,
    }
    r = requests.delete(
        '{}/{}'.format(endpoint_url, slot_dictionary_id),
        headers=headers)
    return platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['message'])
    )


def list_slot_dictionaries(cognito_user,
                           endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['slot_dictionary'])
    headers = {
        'Authorization': cognito_user.access_token,
    }
    r = requests.get(
        endpoint_url,
        headers=headers)
    res = platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['dataId'])
    )
    return res


def update_slot_dictionary(cognito_user, slot_dictionary_id, description,
                           endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['slot_dictionary'])
    slot_dictionary_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, slot_dictionary_id)
    headers = {
        'Authorization': cognito_user.access_token,
        'Content-Type': 'application/json'
    }
    r = requests.put(
        '{}/{}'.format(endpoint_url, slot_dictionary_id),
        json.dumps({
            'description': description
        }),
        headers=headers)
    return platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['message'])
    )


def create_model(cognito_user,
                 training_data_id,
                 algorithm_name,
                 slot_dictionary_id,
                 job_name,
                 description,
                 instance_type,
                 instance_count,
                 volume_size_in_gb,
                 file_path,
                 hyper_parameters,
                 original_model_id,
                 endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['training_job'])
    training_data_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, training_data_id)
    if slot_dictionary_id is not None:
        slot_dictionary_id = attach_user_id_to_resource_id(
            cognito_user.get_user().sub, slot_dictionary_id)
    if original_model_id is not None:
        original_model_id = attach_user_id_to_resource_id(
            cognito_user.get_user().sub, original_model_id)
    param = {
        'trainingDataId': training_data_id,
        'algorithmName': algorithm_name,
        'jobName': job_name,
        'slotDictionaryId': slot_dictionary_id,
        'description': description,
        'instanceType': instance_type,
        'instanceCount': instance_count,
        'volumeSizeInGB': volume_size_in_gb,
        'originalModelId': original_model_id
    }
    # Removes None value from param.
    param = {k: v for k, v in param.items() if v is not None}

    param['hyperParameters'] = {}
    if file_path is not None:
        try:
            with open(file_path) as f:
                param['hyperParameters'] = json.load(f)
        except json.JSONDecodeError as e:
            sys.stderr.write(str(e) + '\n')
            sys.exit(1)
        except FileNotFoundError as e:
            sys.stderr.write(str(e) + '\n')
            sys.exit(1)
        except IsADirectoryError as e:
            sys.stderr.write(str(e) + '\n')
            sys.exit(1)
    else:
        try:
            if hyper_parameters is not None:
                param['hyperParameters'] = json.loads(hyper_parameters)
        except json.JSONDecodeError as e:
            sys.stderr.write(str(e) + '\n')
            sys.exit(1)
    headers = {
        'Authorization': cognito_user.access_token,
        'Content-Type': 'application/json'
    }
    r = requests.post(
        endpoint_url,
        json.dumps(param),
        headers=headers)
    res = platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['modelId', 'message'])
    )
    return res


def read_model(cognito_user, model_id,
               endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['model_metadata'])
    model_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, model_id)
    headers = {
        'Authorization': cognito_user.access_token
    }
    r = requests.get(
        '{}/{}'.format(endpoint_url, model_id),
        headers=headers)
    res = platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r,
            ['modelId', 'trainingDataId', 'message'])
    )
    return res


def update_model(cognito_user, model_id, description,
                 endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['model_metadata'])
    model_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, model_id)
    headers = {
        'Authorization': cognito_user.access_token
    }
    r = requests.put(
        '{}/{}'.format(endpoint_url, model_id),
        json.dumps({
            'description': description
        }),
        headers=headers)
    return platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['message'])
    )


def delete_model(cognito_user, model_id,
                 endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['model_metadata'])
    model_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, model_id)
    headers = {
        'Authorization': cognito_user.access_token
    }
    r = requests.delete(
        '{}/{}'.format(endpoint_url, model_id),
        headers=headers)
    return platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['message'])
    )


def list_models(cognito_user,
                endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['training_job'])
    headers = {
        'Authorization': cognito_user.access_token,
    }
    r = requests.get(
        endpoint_url,
        headers=headers)
    res = platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['modelId', 'trainingDataId'])
    )
    return res


def create_endpoint(cognito_user,
                    model_id,
                    max_capacity=1,
                    slot_dictionary_id=None,
                    endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    model_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, model_id)
    headers = {
        'Authorization': cognito_user.access_token,
        'Content-Type': 'application/json'
    }
    params = {'maxCapacity': max_capacity}
    if slot_dictionary_id:
        slot_dictionary_id = attach_user_id_to_resource_id(
            cognito_user.get_user().sub, slot_dictionary_id)
        params['slotDictionaryId'] = slot_dictionary_id
    r = requests.put(
        '{}/{}/endpoint'.format(endpoint_url, model_id),
        json.dumps(params),
        headers=headers)
    res = platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['endpointId', 'message'])
    )
    return res


def read_intent(cognito_user,
                model_id,
                endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    model_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, model_id)
    headers = {
        'Authorization': cognito_user.access_token
    }
    r = requests.get(
        '{}/{}/intent'.format(endpoint_url, model_id),
        headers=headers)
    return platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['message'])
    )


def read_slot(cognito_user,
              model_id,
              endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    model_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, model_id)
    headers = {
        'Authorization': cognito_user.access_token
    }
    r = requests.get(
        '{}/{}/slot'.format(endpoint_url, model_id),
        headers=headers)
    return platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['message'])
    )


def delete_endpoint(cognito_user,
                    model_id,
                    endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    model_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, model_id)
    headers = {
        'Authorization': cognito_user.access_token
    }
    r = requests.delete(
        '{}/{}/endpoint'.format(endpoint_url, model_id),
        headers=headers)
    return platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['message'])
    )


def inference(cognito_user,
              utterance,
              model_id,
              api_key='',
              slot_dic='',
              endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    model_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, model_id)
    headers = {
        'x-api-key': api_key
    }
    body = {'utterance': utterance}
    if os.path.isfile(slot_dic):
        with open(slot_dic) as f:
            body['slotExpressions'] = json.load(f)

    r = requests.post(
        '{}/{}/endpoint'.format(endpoint_url, model_id),
        json.dumps(body),
        headers=headers)
    return platform.PlatformResponse(
        r.text,
        r.status_code,
        detach_user_id_from_resource_id(
            cognito_user.get_user().sub, r, ['message'])
    )


def get_endpoint_url(cognito_user,
                     endpoint_id,
                     api_key='',
                     endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    endpoint_id = attach_user_id_to_resource_id(
        cognito_user.get_user().sub, endpoint_id)
    headers = {
        'x-api-key': api_key
    }
    url = '{}/{}/endpoint'.format(endpoint_url, endpoint_id)
    r = requests.post(
        url,
        json.dumps({'utterance': 'テスト'}),
        headers=headers)
    res = platform.PlatformResponse(r.text, r.status_code, 'None')
    r_json = res.get_response_body()
    if 'intents' in r_json:
        res.set_message(url)
    return res


def read_remaining_resources(cognito_user, endpoint_url=None):
    endpoint_url = urljoin(
        endpoint_url, ENDPOINT_URL_MAP['remaining_resources'])
    headers = {
        'Authorization': cognito_user.access_token
    }
    r = requests.get(
        '{}/{}'.format(endpoint_url, cognito_user.get_user().sub),
        headers=headers)
    return platform.PlatformResponse(r.text, r.status_code, r.text)


def detach_user_id_from_resource_id(user_id, response, keys):
    """
    keys で指定した response[key] の値の resource_id 部分から user_id の値を削除する。
    Parameters
        user_id: str
            ユーザID
        response: dict or dictのリスト
            APIからのレスポンス
        keys: list
            マスクするresponseのキー
    Returns
        ユーザIDをマスクした結果
    """
    try:
        response = json.loads(response.text)
    except json.JSONDecodeError:
        return response.text
    original_response_type_is_not_list = type(response) is not list
    if not isinstance(response, list):
        response = [response]
    for r in response:
        for key in keys:
            if key in r:
                # 最初に一致するユーザID(システムで付与したユーザID)を削除
                r[key] = r[key].replace(user_id + '-', '', 1)
    if original_response_type_is_not_list:
        response = response[0]
    return json.dumps(response)


def attach_user_id_to_resource_id(user_id, resource_name):
    """
    user_idとresource_nameから、各APIに指定するIDを生成する。
    Parameters
        user_id: str
            ユーザID
        resource_name: str
            リソース名
    Returns
        ユーザIDとリソース名を「-」で結合した値。
    """
    return '{}-{}'.format(user_id, resource_name)
