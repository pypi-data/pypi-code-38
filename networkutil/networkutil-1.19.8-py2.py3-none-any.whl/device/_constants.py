# encoding: utf-8

import attr

DEVICE_CONFIG = u'device_config'


# Device property keys
@attr.s(frozen=True)
class _DeviceConstant(object):
    name = attr.ib(default=u'name', init=False)
    ip = attr.ib(default=u'ip', init=False)
    port = attr.ib(default=u'port', init=False)
    active = attr.ib(default=u'active', init=False)
    default = attr.ib(default=u'default', init=False)


DeviceConstant = _DeviceConstant()

