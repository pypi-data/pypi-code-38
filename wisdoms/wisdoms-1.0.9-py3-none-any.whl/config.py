# Created by Q-ays.
# whosqays@gmail.com

# install PYyaml before use

"""
    Example::

        from wisdoms.config import c
        c.get('name')
"""

import yaml
from wisdoms.utils import joint4path


def read_env(f):
    return f.read().strip()


def read_config(f):
    try:
        return yaml.full_load(f)
    except Exception as e:
        print(e)
        return yaml.load(f)


def find_file(func, path, desc=' '):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            result = func(f)
            if result:
                print('~~~~~~~~~~~~~~~~~~~~~~\033[0;35;0m success \033[0m~~~~~~~~~~~~~~~~~~~~~')
                print('\033[0;32;0m', desc, 'file path is', path, '\033[0m \n')
                return result
            else:
                raise Exception('contents of ' + str(desc) + ' file is None')
    except FileNotFoundError:
        print(desc, 'file path', path, '\033[1;31;0m match failed\033[0m')
        return False


class Config:
    """
    读取yml配置文件
    """

    def __init__(self, layer=4):
        """
        可自动定义层数
        :param layer:
        """

        # find .env file and read
        env_path = '.env'
        env = None
        for i in range(layer):
            env = find_file(read_env, env_path, '.env')

            if env:
                break
            else:
                env_path = joint4path('..', env_path)

        # find config.yml file and read
        self.configuration = None
        if env:
            config_path = joint4path('config', str(env) + '.yml')

            for i in range(layer):
                configuration = find_file(read_config, config_path, 'config.yml')

                if configuration:
                    self.configuration = configuration
                    break
                else:
                    config_path = joint4path('..', config_path)
        else:
            print('~~~~~~~~\033[0;34;0m can not find .env file :< \033[0m~~~~~~~~~~')

    def get(self, key):
        if isinstance(self.configuration, dict):
            return self.configuration[key]
        else:
            return {'err_code': 'maybe environment variable is missed'}

    def to_dict(self):
        if self.configuration:
            return self.configuration


c = Config(5)
