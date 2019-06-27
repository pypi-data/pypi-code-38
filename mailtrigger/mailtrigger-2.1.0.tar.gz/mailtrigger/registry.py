# -*- coding: utf-8 -*-

from .trigger.gerrit import Gerrit
from .trigger.jenkins import Jenkins
from .trigger.jira import Jira
from .trigger.printer import Printer

REGISTRY = [
    {
        'class': Gerrit,
        'name': Gerrit.__name__.lower()
    },
    {
        'class': Jenkins,
        'name': Jenkins.__name__.lower()
    },
    {
        'class': Jira,
        'name': Jira.__name__.lower()
    },
    {
        'class': Printer,
        'name': Printer.__name__.lower()
    }
]


class RegistryException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Registry(object):
    def __init__(self, config):
        self._config = config
        self._registry = self._build(REGISTRY)

    @staticmethod
    def _build(registry):
        from .trigger.helper import Helper
        registry.append({
            'class': Helper,
            'name': Helper.__name__.lower()
        })
        return registry

    def instantiate(self):
        instance = []
        for item in self._registry:
            config = self._config.get(item['name'], None)
            if config is not None:
                config['debug'] = self._config['debug']
                instance.append(item['class'](config))
        if len(instance) == 0:
            raise RegistryException('invalid trigger configuration')
        return instance
