class DataFormatter:
    @classmethod
    def from_default(cls, device, param, value):
        return value

    @classmethod
    def get_register_count(cls, device, param_id):
        raise NotImplemented('{0}.{1}'.format(cls.__name__, 'get_register_count'))

    @classmethod
    def encode(cls, device, param, value):
        raise NotImplemented('{0}.{1}'.format(cls.__name__, 'encode'))

    @classmethod
    def decode(cls, device, param, value):
        raise NotImplemented('{0}.{1}'.format(cls.__name__, 'decode'))


class DataFormatterInteger(DataFormatter):
    @classmethod
    def from_default(cls, device, param, value):
        return int(value)

    @classmethod
    def get_register_count(cls, device, param):
        return param.get('reg_count', 1)

    @classmethod
    def encode(cls, device, param, value):
        return value  # .to_bytes(cls.get_register_count(device, param), byteorder=param.get('reg_byteorder', 'big'))

    @classmethod
    def decode(cls, device, param, value):
        if param.get('reg_count', 1) == 1:
            return value[0]
        else:
            raise Exception('Unsupported type')
        # return int.from_bytes(value, byteorder=param.get('reg_byteorder', 'big'))


class DataFormatterString(DataFormatter):

    @classmethod
    def get_register_count(cls, device, param):
        return param.get('maximum', 1)

    @classmethod
    def decode(cls, device, param, value):
        result = ''
        for elem in value:
            result += chr(elem)
        return result.strip()


class DataFormatterArray(DataFormatter):
    @classmethod
    def from_default(cls, device, param, value):
        result = []
        item_param = device.config[param['pattern']]
        item_formatter = device.get_formatter(item_param['formatter'])
        for elem in value.split(','):
            result.append(item_formatter.from_default(device, item_param, elem))
        return result

    @classmethod
    def get_register_count(cls, device, param):
        item_param = device.config[param['pattern']]
        item_formatter = device.get_formatter(item_param['formatter'])
        return item_formatter.get_register_count(device, item_param) * param['maximum']

    @classmethod
    def encode(cls, device, param, value):
        result = []
        item_param = device.config[param['pattern']]
        item_formatter = device.get_formatter(item_param['formatter'])
        for _value in value:
            result.append(item_formatter.encode(device, item_param, _value))
        return result

    @classmethod
    def decode(cls, device, param, value):
        item_param = device.config[param['pattern']]
        item_formatter = device.get_formatter(item_param['formatter'])
        size = item_formatter.get_register_count(device, item_param)
        result = []
        while value:
            result.append(item_formatter.decode(device, item_param, value[0: size]))
            value = value[size:]
        return result


class DataFormatterBoolean(DataFormatter):
    @classmethod
    def from_default(cls, device, param, value):
        return 1 if value else 0

    @classmethod
    def get_register_count(cls, device, param):
        return 1

    @classmethod
    def encode(cls, device, param, value):
        return [value]

    @classmethod
    def decode(cls, device, param, value):
        return True if value[0] else False
