import json
from typing import Dict


class DeploymentOutputConverter:
    @staticmethod
    def convert_from_terraform_output(output_json: {}) -> Dict[str, str]:
        res = {}
        for k, v in output_json.items():
            output_type = v['type']
            if output_type == 'map' or output_type == 'list':
                res[k] = json.dumps(v['value'])
            else:
                res[k] = v['value']
        return res

    @staticmethod
    def convert_from_configuration_script(output: str) -> Dict[str, str]:
        res = dict()
        for line in output.splitlines():
            split = str.split(line, '=')
            name = split[0].strip()
            value = split[1].strip()
            res[name] = value
        return res
