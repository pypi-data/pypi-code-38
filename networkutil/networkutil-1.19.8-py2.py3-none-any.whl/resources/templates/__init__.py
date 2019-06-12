# encoding: utf-8

import os

base_dir = u'{dir}{sep}'.format(dir=os.path.dirname(os.path.realpath(__file__)),
                                sep=os.sep)

endpoints = u'{base}{filename}'.format(base=base_dir, filename=u'endpoints.json')
jumpbox = u'{base}{filename}'.format(base=base_dir, filename=u'jumpbox.json')
environments_layout = u'{base}{filename}'.format(base=base_dir, filename=u'environments_layout.json')
api_layout = u'{base}{filename}'.format(base=base_dir, filename=u'api_layout.json')
endpoint_layout = u'{base}{filename}'.format(base=base_dir, filename=u'endpoint_layout.json')
endpoint_launcher_layout = u'{base}{filename}'.format(base=base_dir, filename=u'endpoint_launcher_layout.json')
devices = u'{base}{filename}'.format(base=base_dir, filename=u'devices.yaml')
ssl = u'{base}{filename}'.format(base=base_dir, filename=u'ssl.json')
