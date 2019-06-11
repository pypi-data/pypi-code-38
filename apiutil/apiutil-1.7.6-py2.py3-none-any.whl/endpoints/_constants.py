# encoding: utf-8

import attr

__all__ = ['ENVIRONMENT_CONFIG',
           'API_CONFIG',
           'HOST_CONFIG',
           'ENDPOINT_CONFIG',
           'HostKeysConstant',
           'EndpointKeysConstant',
           'APIKeysConstant',
           'EnvironmentKeysConstant']

# Config Params
ENVIRONMENT_CONFIG = u'environments'
API_CONFIG = u'apis'
HOST_CONFIG = u'hosts'
ENDPOINT_CONFIG = u'endpoints'


# Object Keys Constants
@attr.s(frozen=True)
class _HostKeysConstant(object):
    protocol = attr.ib(default=u'protocol', init=False)
    domain = attr.ib(default=u'domain', init=False)
    port = attr.ib(default=u'port', init=False)
    secret_key = attr.ib(default=u'secret_key', init=False)
    user = attr.ib(default=u'user', init=False)
    password = attr.ib(default=u'password', init=False)


HostKeysConstant = _HostKeysConstant()


@attr.s(frozen=True)
class _EndpointKeysConstant(object):
    path = attr.ib(default=u'path', init=False)
    params = attr.ib(default=u'params', init=False)


EndpointKeysConstant = _EndpointKeysConstant()


@attr.s(frozen=True)
class _APIKeysConstant(object):
    family = attr.ib(default=u'family', init=False)
    host = attr.ib(default=u'host', init=False)
    endpoints = attr.ib(default=u'endpoints', init=False)
    params = attr.ib(default=u'params', init=False)


APIKeysConstant = _APIKeysConstant()


@attr.s(frozen=True)
class _EnvironmentKeysConstant(object):
    location = attr.ib(default=u'location', init=False)
    apis = attr.ib(default=u'apis', init=False)


EnvironmentKeysConstant = _EnvironmentKeysConstant()
