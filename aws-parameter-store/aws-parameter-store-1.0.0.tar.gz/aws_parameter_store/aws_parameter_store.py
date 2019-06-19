import json
import logging
from typing import List, Tuple, Any, Callable, Dict

import boto3

PATH_DELIMITER = "/"
logger = logging.getLogger(__name__)


class AwsParameterStore:
    def __init__(self, region: str, **kwargs):
        kwargs["region_name"] = region
        self.client = boto3.client("ssm", **kwargs)

    @staticmethod
    def _aws_paginated_call(paginated_sdk_call: Callable, data_filter: str, **kwargs) -> List:
        data = []
        while True:
            result = paginated_sdk_call(**kwargs)
            data += result[data_filter]
            next_token = result.get("NextToken")
            if next_token is None:
                break
            kwargs["NextToken"] = next_token
        return data

    def _parameter_res_to_dict(self, parameters_list: List, get_flat_dict: bool = False) -> Dict:
        parameters_dict = {}

        for param in parameters_list:
            [key, val] = self._strip_param(param)
            parameters_dict[key] = val

        if get_flat_dict:
            return parameters_dict

        return self._flat_dict_to_nested(parameters_dict)

    def _flat_dict_to_nested(self, parameters_dict: Dict) -> Dict:
        ret = {}
        for recursive_key, value in parameters_dict.items():
            for key in reversed(recursive_key.split(PATH_DELIMITER)):
                value = {key: value}
            self._merge(ret, value)
        return ret

    @staticmethod
    def _merge(base_dict: Dict, update_dict: Dict, path=None):
        if path is None:
            path = []
        for key in update_dict:
            if key in base_dict:
                if isinstance(base_dict[key], dict) and isinstance(update_dict[key], dict):
                    AwsParameterStore._merge(base_dict[key], update_dict[key], path + [str(key)])
                elif base_dict[key] == update_dict[key]:
                    pass
                else:
                    raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
            else:
                base_dict[key] = update_dict[key]
        return base_dict

    def _strip_param(self, parameter) -> Tuple[str, Any]:
        name = parameter["Name"]
        key = name.split(self.namespace)[1]
        str_val = parameter["Value"]
        try:
            value = json.loads(str_val)
        except ValueError:
            value = str_val

        return key, value

    def get_parameters_dict(self, namespace: str = '/', decrypt: bool = True, get_flat_dict: bool = False) -> Dict:
        """Get all parameters under certain namespace,
        structured as a nested dictionary.
        """
        self.namespace = namespace if namespace.endswith(PATH_DELIMITER) else namespace + PATH_DELIMITER
        kwargs = dict(Path=namespace, Recursive=True, WithDecryption=decrypt)

        try:
            parameter_res = self._aws_paginated_call(
                paginated_sdk_call=self.client.get_parameters_by_path, data_filter="Parameters", **kwargs
            )
        except Exception as error:
            logger.error(error)
            raise

        return self._parameter_res_to_dict(parameter_res, get_flat_dict)
