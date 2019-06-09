import json
from pathlib import Path

import jsonschema
import torch.nn as nn

from .configs import GroupRuleConfig


class GroupRule(GroupRuleConfig):
    with open(str(Path(__file__).parent / 'schema' / 'group_rule_config.json')) as f:
        schema = json.load(f)

    def __init__(self, config: dict):
        super().__init__(values=config)

        self.module_type_set = set(self.module_type_list)
        self.module_name_set = set(self.module_name_list)
        self.param_name_set = set(self.param_name_list)

    def match(self, module: nn.Module, name: str, param_name: str = None, prefix: str = None):
        module_type = module.__class__.__name__
        module_match = (not self.module_type_set or module_type in self.module_type_set)
        name_match = (not self.module_name_set or name in self.module_name_set)
        param_match = (not self.param_name_set or param_name in self.param_name_set)
        prefix_match = (not self.prefix_list or any(prefix.startswith(p) for p in self.prefix_list))
        return module_match and name_match and param_match and prefix_match

    @classmethod
    def factory(cls, config: dict = None):
        jsonschema.validate(config or {}, cls.schema)
        return cls(config=config)
