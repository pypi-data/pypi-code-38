import os
from sanic.config import Config


def load_config():
    conf = Config()
    module = os.environ.get('SANIC_SETTINGS_MODULE', 'settings')
    if module:
        path = '{}.py'.format(module.replace('.', '/'))
        conf.from_pyfile(path)
    return conf
