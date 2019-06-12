# encoding: utf-8

import os

base_dir = u'{dir}{sep}'.format(dir=os.path.dirname(os.path.realpath(__file__)),
                                sep=os.sep)

endpoints = u'{base}{filename}'.format(base=base_dir, filename=u'endpoints.json')
jumpbox = u'{base}{filename}'.format(base=base_dir, filename=u'jumpbox.json')
devices = u'{base}{filename}'.format(base=base_dir, filename=u'devices.json')
ssl = u'{base}{filename}'.format(base=base_dir, filename=u'ssl.json')
