import json
from pathlib import Path
from typing import Type

import box
import jsonschema
import torch.nn
import torch.optim

from .configs import OptimizerConfig
from .group_parameters import group_parameters
from .group_rule import GroupRule

# register common optimizers
box.register(torch.optim.SGD, tag='optimizer')
box.register(torch.optim.Adam, tag='optimizer')
box.register(torch.optim.RMSprop, tag='optimizer')

with open(str(Path(__file__).parent / 'schema' / 'optimizer_config.json')) as f:
    schema = json.load(f)


def optimizer_factory(model: torch.nn.Module, config: dict = None) -> torch.optim.Optimizer:
    jsonschema.validate(config or {}, schema)
    config = OptimizerConfig(config)

    rules = list(map(GroupRule.factory, config.rules))
    param_groups = group_parameters(model=model, rules=rules)

    params = []
    for param_group, rule in zip(param_groups, rules):
        if rule.refuse_if_match is False:
            params.append({
                'params': param_group,
                **rule.kwargs
            })

    optimizer_class: Type[torch.optim.Optimizer] = box.load(config.type, tag='optimizer')
    return optimizer_class(params=params, lr=config.lr, **config.kwargs)
