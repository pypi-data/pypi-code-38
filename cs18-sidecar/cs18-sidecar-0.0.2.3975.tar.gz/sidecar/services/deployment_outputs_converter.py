import json
from abc import abstractmethod, ABCMeta
from logging import Logger
from typing import Dict


class OutputValueToStringConverter(metaclass=ABCMeta):

    @abstractmethod
    def convert_to_str(self, value_type: str, value):
        raise NotImplemented()

    @abstractmethod
    def can_handle(self, value_type: str) -> bool:
        raise NotImplemented()


class StrValueToStringConverter(OutputValueToStringConverter):

    def convert_to_str(self, value_type: str, value):
        return value

    def can_handle(self, value_type: str) -> bool:
        return value_type == "str"


class JsonValueToStringConverter(OutputValueToStringConverter):
    def convert_to_str(self, value_type: str, value):
        return json.dumps(value)

    def can_handle(self, value_type: str) -> bool:
        return value_type == 'json'


class OutputValueToStringConverterFactory:

    def __init__(self):
        self.converters = [JsonValueToStringConverter(), StrValueToStringConverter()]

    def convert_to_str(self, value_type: str, value):
        converter = next((c for c in self.converters if c.can_handle(value_type)), None)
        if not converter:
            raise Exception(f'no converter define for value type: {value_type}')
        return converter.convert_to_str(value_type, value)


class DeploymentOutputsConverter:

    @staticmethod
    def convert_from_terraform_outputs(outputs_json: {}) -> Dict[str, Dict]:
        res = {}
        for k, v in outputs_json.items():
            output_type = v['type']
            value = v['value']
            if output_type == "map" or output_type == "list":
                value_type = 'json'
            else:
                value_type = 'str'

            res[k] = {
                "type": value_type,
                "value": value
            }
        return res

    @staticmethod
    def convert_from_configuration_script(outputs: str) -> Dict[str, Dict]:
        res = dict()
        for line in outputs.splitlines():
            split = str.split(line, '=')
            name = split[0].strip()
            value = split[1].strip()
            res[name] = {
                "type": "str",
                "value": value
            }
        return res
