from collections import OrderedDict
from typing import Type

import torch.nn as nn


class ModuleTag(nn.Module):
    def __init__(self, core: nn.Module):
        super().__init__()
        self.core = core

    def forward(self, *args, **kwargs):  # pragma: no cover
        return self.core(*args, **kwargs)


class ModuleTagHelper(nn.Module):
    def forward(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError

    def named_parameters_with_tag(self, memo=None, prefix='', tag: Type[ModuleTag] = None):
        if isinstance(self, ModuleTag):
            tag = type(self)

        if memo is None:
            memo = set()
        for name, p in self._parameters.items():
            if p is not None and p not in memo:
                memo.add(p)
                yield prefix + ('.' if prefix else '') + name, p, tag
        for mname, module in self.named_children():
            submodule_prefix = prefix + ('.' if prefix else '') + mname
            for name, p, t in ModuleTagHelper.named_parameters_with_tag(module, memo, submodule_prefix, tag):
                yield name, p, t

    def state_dict_with_tag(self, destination=None, prefix='', tag: Type[ModuleTag] = None, keep_vars=False):
        if isinstance(self, ModuleTag):
            tag = type(self)

        if destination is None:
            destination = OrderedDict()
            destination._metadata = OrderedDict()
        destination._metadata[prefix[:-1]] = dict(version=self._version)
        for name, param in self._parameters.items():
            if param is not None:
                destination[prefix + name] = (param if keep_vars else param.data, tag)
        for name, buf in self._buffers.items():
            if buf is not None:
                destination[prefix + name] = (buf if keep_vars else buf.data, tag)
        for name, module in self._modules.items():
            if module is not None:
                ModuleTagHelper.state_dict_with_tag(
                    module, destination, prefix + name + '.', tag=tag, keep_vars=keep_vars
                )
        return destination


def named_parameters_with_tag(module: nn.Module, prefix=''):
    # noinspection PyCallByClass
    return ModuleTagHelper.named_parameters_with_tag(module, prefix=prefix)


def state_dict_with_tag(module: nn.Module, prefix='', keep_vars=False):
    # noinspection PyCallByClass
    return ModuleTagHelper.state_dict_with_tag(module, prefix=prefix, keep_vars=keep_vars)


class SpecialSync(ModuleTag):
    pass
