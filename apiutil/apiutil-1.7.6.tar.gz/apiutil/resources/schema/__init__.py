# encoding: utf-8

import os

base_dir = u'{dir}{sep}'.format(dir=os.path.dirname(os.path.realpath(__file__)),
                                sep=os.sep)

api_config = u'{base}{filename}'.format(base=base_dir, filename=u'api_config.json')
environment_config = u'{base}{filename}'.format(base=base_dir, filename=u'environment_config.json')
host_config = u'{base}{filename}'.format(base=base_dir, filename=u'host_config.json')
endpoint_config = u'{base}{filename}'.format(base=base_dir, filename=u'endpoint_config.json')
