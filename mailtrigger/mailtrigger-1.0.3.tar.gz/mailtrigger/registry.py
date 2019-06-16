# -*- coding: utf-8 -*-

from .trigger.gerrit import Gerrit
from .trigger.jenkins import Jenkins
from .trigger.jira import Jira

REGISTRY = [
    {
        'class': Gerrit,
        'host': '',
        'name': Gerrit.__name__.lower(),
        'port': ''
    },
    {
        'class': Jenkins,
        'host': '',
        'name': Jenkins.__name__.lower(),
        'port': ''
    },
    {
        'class': Jira,
        'host': '',
        'name': Jira.__name__.lower(),
        'port': ''
    }
]


class Registry(object):
    def __init__(self):
        self._registry = REGISTRY

    def _set_debug(self, config, name):
        for index in range(len(self._registry)):
            self._registry[index]['debug'] = config[name]

    def _set_trigger(self, config, name):
        for index in range(len(self._registry)):
            if name == self._registry[index]['name']:
                self._registry[index]['host'] = config[name].get('host', '')
                self._registry[index]['port'] = config[name].get('port', '')

    def fill(self, config):
        for key in config.keys():
            if key == 'debug':
                self._set_debug(config, key)
            else:
                self._set_trigger(config, key)

    def list(self):
        return [r['name'] for r in self._registry]

    def query(self, name):
        trigger = None
        for item in self._registry:
            if item['name'] == name:
                trigger = item
                break
        return trigger
