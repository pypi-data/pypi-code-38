import base64
import json
import os
import pickle
import threading
import time

import requests

ADD_SNAP_URL = 'https://www.varsnap.com/add_snap/'
GET_SNAP_URL = 'https://www.varsnap.com/get_snap/'

# Names of different environment variables used by varsnap
# See readme for descriptions
ENV_VARSNAP = 'VARSNAP'
ENV_ENV = 'ENV'
ENV_AUTH_TOKEN = 'VARSNAP_TOKEN'


def env_var(env):
    return os.environ.get(env, '').lower()


def should_receive():
    if env_var(ENV_VARSNAP) != 'true':
        return False
    if env_var(ENV_ENV) != 'development':
        return False
    if not env_var(ENV_AUTH_TOKEN):
        return False
    return True


def should_send():
    if env_var(ENV_VARSNAP) != 'true':
        return False
    if env_var(ENV_ENV) != 'production':
        return False
    if not env_var(ENV_AUTH_TOKEN):
        return False
    return True


def serialize(data):
    data = base64.b64encode(pickle.dumps(data)).decode('utf-8')
    return data


def deserialize(data):
    data = pickle.loads(base64.b64decode(data.encode('utf-8')))
    return data


def send_snap(args, kwargs, output):
    if not should_send():
        return
    data = {
        'auth_token': env_var(ENV_AUTH_TOKEN),
        'inputs': serialize([args, kwargs]),
        'prod_outputs': serialize(output)
    }
    requests.post(ADD_SNAP_URL, data=data)


def ping_prod(func):
    seen = {}
    while True:
        data = {
            'auth_token': env_var(ENV_AUTH_TOKEN),
        }
        response = requests.post(GET_SNAP_URL, data=data)
        response_data = json.loads(response.content)
        if response_data:
            if response_data['inputs'] in seen:
                time.sleep(1)
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
        time.sleep(0.1)


def varsnap(func):
    if should_receive():
        threading.Thread(target=ping_prod, args=(func,)).start()

    def magic(*args, **kwargs):
        # TODO - Make magic
        try:
            output = func(*args, **kwargs)
        except Exception as e:
            # TODO - distinguish between raised errors versus returned errors
            threading.Thread(target=send_snap, args=(args, kwargs, e)).start()
        threading.Thread(target=send_snap(args, kwargs, output)).start()
        return output
    return magic
