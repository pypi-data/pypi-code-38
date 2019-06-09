from typing import Iterator, List, Tuple

import torch.nn as nn

from .group_rule import GroupRule


def named_parameters(module: nn.Module, prefix: str = '') -> Iterator[Tuple[str, nn.Parameter]]:
    memo = set()
    for name, p in module._parameters.items():
        if p is not None and p not in memo:
            memo.add(p)
            yield f'{prefix}.{name}' if prefix else name, p


def group_parameters(model: nn.Module, rules: List[GroupRule]) -> List[List[nn.Parameter]]:
    results: List[list] = [[] for _ in rules]

    def dfs(module: nn.Module, module_name: str = None, prefix: str = '', match_level: int = None):
        new_match_level = None
        for i, rule in enumerate(rules[:match_level]):
            if rule.match(module, module_name):
                new_match_level = i + 1
                break
        if new_match_level is None:
            new_match_level = match_level

        for name, child in module.named_children():
            dfs(child, name, prefix=f'{prefix}.{name}' if prefix else name, match_level=new_match_level)

        for name, param in named_parameters(module=module):
            new_prefix = f'{prefix}.{name}' if prefix else name
            for i, rule in enumerate(rules[:match_level]):
                if rule.match(module, module_name, param_name=name, prefix=new_prefix):
                    results[i].append(param)
                    break
            else:
                if new_match_level is not None:
                    results[new_match_level - 1].append(param)

    dfs(model)
    return results
