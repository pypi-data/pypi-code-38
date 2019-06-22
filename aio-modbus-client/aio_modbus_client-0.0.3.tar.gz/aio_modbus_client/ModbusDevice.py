from .DataFormatter import *
from .ModbusDeviceMixin import ModbusDeviceMixin
import os
import json
import logging

_logger = logging.getLogger(__name__)


class ModbusDevice(ModbusDeviceMixin):
    file = __file__
    # formatter = DataFormatter
    pass

    def __init__(self, address, protocol, **kwargs):
        ModbusDeviceMixin.__init__(self, address, protocol, **kwargs)

    async def read_param(self, param_id):
        _logger.debug('read_param({})'.format(param_id))
        param = self.config[param_id]
        return await getattr(self, '_read_{}'.format(param['table']))(param_id, param)

    async def write_param(self, param_id, value):
        _logger.debug('write_param({})'.format(param_id))
        param = self.config[param_id]
        return await getattr(self, '_write_{}'.format(param['table']))(param_id, param, value)

    async def close(self):
        await self.protocol.close()

    async def is_device(self):
        raise NotImplemented()

    async def find_devices(self):
        result = []
        current_slave_id = self.slave_id
        for i in range(253):
            self.slave_id = i + 1
            print(self.slave_id)
            try:
                if await self.is_device():
                    result.append(self.slave_id)
            except Exception as e:
                pass
        self.slave_id = current_slave_id
        return result
