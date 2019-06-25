import sys
import types

import pluggy

from . hookspecs import hookimpl, fsx_get_module_dict, fsx_get_fake_module_dict


__all__ = [
    'load',
    'monkeypatch_to_fake_modules',
    'hookimpl',
    'fsx_get_module_dict',
    'fsx_get_fake_module_dict',
]


def load():
    module_dicts = _get_plugin_manager().hook.fsx_get_module_dict()
    for module_dict in module_dicts:
        for module_name, module in module_dict.items():
            # Makes `import fsx.<<plugin>>` work.
            sys.modules['fsx.'+module_name] = types.ModuleType('fsx.'+module_name)

            # Ensure accessing `fsx.<<plugin>>` works.
            setattr(sys.modules['fsx'], module_name, module)

def monkeypatch_to_fake_modules(monkeypatch, fsx_fake):
    plugin_manager = _get_plugin_manager()
    fake_module_dicts = plugin_manager.hook.fsx_get_fake_module_dict(fsx_fake_tree=fsx_fake)
    for fake_module_dict in fake_module_dicts:
        for module_name, fake_func_dict in fake_module_dict.items():
            fsx_submodule = getattr(fsx, module_name)
            for func_name, fake_func in fake_func_dict.items():
                monkeypatch.setattr(fsx_submodule, func_name, fake_func)

def _get_plugin_manager():
    res = pluggy.PluginManager('fsx')
    res.add_hookspecs(hookspecs)
    res.load_setuptools_entrypoints('fsx')
    return res

