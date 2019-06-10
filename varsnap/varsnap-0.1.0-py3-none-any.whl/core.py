import asyncio
import base64
import json
import os
import pickle

import requests

ADD_SNAP_URL = 'https://www.varsnap.com/add_snap/'
GET_SNAP_URL = 'https://www.varsnap.com/get_snap/'
ENV_VAR = {
    'varsnap': os.environ.get('VARSNAP', '').lower(),
    'env': os.environ.get('ENV', '').lower(),
    'auth_token': os.environ.get('VARSNAP_TOKEN', '').lower(),
}


def should_receive():
    if ENV_VAR['varsnap'] != 'true':
        return False
    if ENV_VAR['env'] != 'development':
        return False
    if not ENV_VAR['auth_token']:
        return False
    return True


def should_send():
    if ENV_VAR['varsnap'] != 'true':
        return False
    if ENV_VAR['env'] != 'production':
        return False
    if not ENV_VAR['auth_token']:
        return False
    return True


def serialize(data):
    data = base64.b64encode(pickle.dumps(data)).decode('utf-8')
    return data


def deserialize(data):
    data = pickle.loads(base64.b64decode(data.encode('utf-8')))
    return data


async def send_snap(args, kwargs, output):
    if not should_send():
        return
    data = {
        'auth_token': ENV_VAR['auth_token'],
        'inputs': serialize([args, kwargs]),
        'prod_outputs': serialize(output)
    }
    requests.post(ADD_SNAP_URL, data=data)


async def ping_prod(func):
    seen = {}
    while True:
        data = {
            'auth_token': ENV_VAR['auth_token'],
        }
        response = requests.post(GET_SNAP_URL, data=data)
        response_data = json.loads(response.content)
        if response_data:
            if response_data['inputs'] in seen:
                await asyncio.sleep(1)
                continue
            seen[response_data['inputs']] = response_data['prod_outputs']
            inputs = deserialize(response_data['inputs'])
            prod_outputs = deserialize(response_data['prod_outputs'])
            print('input:        ', inputs[0])
            print('prod_outputs: ', prod_outputs)
            output = func(*inputs[0], **inputs[1])
            print('dev_outputs:  ', output)
            print('correct:      ', prod_outputs == output)
            print('')
        await asyncio.sleep(0.1)


def varsnap(func):
    if should_receive():
        asyncio.run(ping_prod(func))

    def magic(*args, **kwargs):
        # TODO - Make magic
        try:
            output = func(*args, **kwargs)
        except Exception as e:
            # TODO - distinguish between raised errors versus returned errors
            asyncio.run(send_snap(args, kwargs, e))
        asyncio.run(send_snap(args, kwargs, output))
        return output
    return magic
