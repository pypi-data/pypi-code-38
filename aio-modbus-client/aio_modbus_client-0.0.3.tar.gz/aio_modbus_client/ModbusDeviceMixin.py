from .DataFormatter import *
from .InputRegister import ReadInputRegistersRequest
from .CoilsRegister import ReadCoilsRequest, WriteMultipleCoilsRequest
from .HoldingRegister import ReadHoldingRegistersRequest, WriteSingleRegisterRequest, WriteMultipleRegistersRequest
import os
import json
import logging
_logger = logging.getLogger(__name__)


class ModbusDeviceMixin:
    file = __file__
    formatter = {
        'integer': DataFormatterInteger,
        'string': DataFormatterString,
        'array': DataFormatterArray,
        'boolean': DataFormatterBoolean,
    }

    def __init__(self, slave_id, protocol, **kwargs):
        self.protocol = protocol
        self.slave_id = slave_id
        pass
        self.serial = dict(
            baudRate=kwargs.get('baudRate', 9600),
            parity=kwargs.get('parity', 0),
            dataBits=kwargs.get('dataBits', 8),
            stopBits=kwargs.get('stopBits', 1)
        )
        self.config = self.load_config()
        self.data = self.get_default_data()

    def get_default_data(self):
        data = {}
        for elem in self.config:
            try:
                data[elem] = self.get_default_param_value(elem)
            except KeyError:
                pass
        return data

    def get_default_param_value(self, param_name):
        formatter = self.get_formatter(self.config[param_name]['formatter'])
        return formatter.from_default(self, self.config[param_name], self.config[param_name]['default'])

    def load_config(self):
        config_path = '{0}/{1}.json'.format(os.path.dirname(self.file), self.__class__.__name__)
        try:
            with open(os.path.normpath(config_path), 'r', encoding='utf-8') as file:
                raw_data = json.load(file)
            config = {}
            if raw_data:
                for elem in raw_data:
                    config[elem['id']] = elem
            return config
        except Exception as e:
            raise Exception('Error load config {0}: {1}'.format(config_path, e))

    def get_formatter(self, name):
        try:
            return self.formatter[name]
        except KeyError:
            raise Exception('Invalid parameter format \'{format}\'. Permissible: {values}'.format(
                format=name,
                values=str(list(self.formatter.keys()))
            ))

    async def _read_calc(self, param_id, param):
        return await getattr(self, '_read_calc_{}'.format(param_id))(param_id, param)

    async def _read_input(self, param_id, param):
        formatter = self.get_formatter(param['formatter'])
        request = ReadInputRegistersRequest(
            self.slave_id,
            param['address'],
            formatter.get_register_count(self, param),
        )
        response = await self.protocol.execute(request, self.serial)
        # response = await request.execute(self)
        return formatter.decode(self, param, response.registers)

    async def _read_holding(self, param_id, param):
        formatter = self.get_formatter(param['formatter'])
        request = ReadHoldingRegistersRequest(
            self.slave_id,
            param['address'],
            formatter.get_register_count(self, param)
        )
        # response = await request.execute(self)
        response = await self.protocol.execute(request, self.serial)
        return formatter.decode(self, param, response.registers)

    async def _read_coil(self, param_id, param):
        formatter = self.get_formatter(param['formatter'])
        request = ReadCoilsRequest(
            self.slave_id,
            param['address'],
            formatter.get_register_count(self, param)
        )
        response = await self.protocol.execute(request, self.serial)
        # response = await request.execute(self)
        if isinstance(response, Exception):
            raise response
        return formatter.decode(self, param, response.bits)

    async def _write_calc(self, param_id, param, value):
        return await getattr(self, '_write_calc_{}'.format(param_id))(param_id, param, value)

    async def _write_holding(self, param_id, param, value):
        formatter = self.get_formatter(param['formatter'])
        if isinstance(value, list):
            request = WriteMultipleRegistersRequest(
                self.slave_id,
                param['address'],
                formatter.encode(self, param, value)
            )
        else:
            request = WriteSingleRegisterRequest(
                self.slave_id,
                param['address'],
                formatter.encode(self, param, value)
            )
        response = await self.protocol.execute(request, self.serial)
        # response = await request.execute(self)
        return True

    async def _write_coil(self, param_id, param, value):
        formatter = self.get_formatter(param['formatter'])
        request = WriteMultipleCoilsRequest(
            self.slave_id,
            param['address'],
            formatter.encode(self, param, value)
        )
        response = await self.protocol.execute(request, self.serial)
        # response = await request.execute(self)
        return True

    def _change_data(self, data):
        self.data.update(data)
