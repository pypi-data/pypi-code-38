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


class Producer():
    @staticmethod
    def is_enabled():
        if env_var(ENV_VARSNAP) != 'true':
            return False
        if env_var(ENV_ENV) != 'production':
            return False
        if not env_var(ENV_AUTH_TOKEN):
            return False
        return True

    @staticmethod
    def serialize(data):
        data = base64.b64encode(pickle.dumps(data)).decode('utf-8')
        return data

    @staticmethod
    def produce(args, kwargs, output):
        if not Producer.is_enabled():
            return
        data = {
            'auth_token': env_var(ENV_AUTH_TOKEN),
            'inputs': Producer.serialize([args, kwargs]),
            'prod_outputs': Producer.serialize(output)
        }
        requests.post(ADD_SNAP_URL, data=data)


class Consumer():
    @staticmethod
    def is_enabled():
        if env_var(ENV_VARSNAP) != 'true':
            return False
        if env_var(ENV_ENV) != 'development':
            return False
        if not env_var(ENV_AUTH_TOKEN):
            return False
        return True

    @staticmethod
    def deserialize(data):
        data = pickle.loads(base64.b64decode(data.encode('utf-8')))
        return data

    @staticmethod
    def consume(func):
        if not Consumer.is_enabled():
            return
        last_snap_id = ''
        while True:
            data = {
                'auth_token': env_var(ENV_AUTH_TOKEN),
            }
            response = requests.post(GET_SNAP_URL, data=data)
            try:
                response_data = json.loads(response.content)
            except json.decoder.JSONDecodeError:
                response_data = ''
            if not response_data:
                time.sleep(1)
                continue
            if response_data['id'] == last_snap_id:
                time.sleep(1)
                continue
            last_snap_id = response_data['id']
            inputs = Consumer.deserialize(response_data['inputs'])
            prod_outputs = Consumer.deserialize(response_data['prod_outputs'])
            print('input:        ', inputs[0])
            print('prod_outputs: ', prod_outputs)
            output = func(*inputs[0], **inputs[1])
            print('dev_outputs:  ', output)
            print('correct:      ', prod_outputs == output)
            print('')


def varsnap(func):
    thread = threading.Thread(target=Consumer.consume, args=(func,))
    thread.daemon = True
    thread.start()

    def magic(*args, **kwargs):
        try:
            output = func(*args, **kwargs)
        except Exception as e:
            threading.Thread(
                target=Producer.produce,
                args=(args, kwargs, e),
            ).start()
            raise
        threading.Thread(
            target=Producer.produce,
            args=(args, kwargs, output),
        ).start()
        return output
    return magic
