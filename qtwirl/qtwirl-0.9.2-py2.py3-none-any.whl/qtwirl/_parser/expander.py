# Tai Sakuma <tai.sakuma@gmail.com>
"""

A generic tool to expand config written in dict and a list of dict.

This module is not specific to qtwirl and can become an independent
package in the future.


"""

import logging
import functools
import copy

from .._misc import is_dict

##__________________________________________________________________||
__all__ = ['config_expander']

##__________________________________________________________________||
def config_expander(expand_func_map=None, config_keys=None,
                    default_config_key=None, default_cfg_dict=None):
    """return a function that expands a config

    Parameters
    ----------
    expand_func_map : dict, optional
        A map from a config key to a function 1) that expands the
        config for the key or 2) that updates the shared objects

    config_keys : list, optional
        A list of extra config keys that are not in keys of
        ``expand_func_map``.

    default_config_key: str, optional
        A default key

    default_cfg_dict: dict, optional
        A dict of default config

    Returns
    -------
    function
        A function that expands a config

    """

    #
    if expand_func_map is None:
        expand_func_map = {}

    if config_keys is None:
        config_keys = []

    if default_cfg_dict is None:
        default_cfg_dict = {}

    #
    expand_func_map = expand_func_map.copy() # so as not to modify
                                                 # the original

    #
    if 'set_default' in expand_func_map:
        logger = logging.getLogger(__name__)
        msg = '"set_default" is in expand_func_map: expand_func_map={!r}'.format(expand_func_map)
        logger.info(msg)
    else:
        expand_func_map['set_default'] = _set_default

    #
    config_keys = set(config_keys)
    config_keys.update(expand_func_map.keys())

    if default_config_key is not None:
        config_keys.add(default_config_key)

    #
    default_cfg_dict = _wrap_default_cfg(default_cfg_dict, config_keys, default_config_key)
    default_cfg_stack = [default_cfg_dict]

    #
    shared = dict(
        default_cfg_stack=default_cfg_stack,
        expand_func_map=expand_func_map,
        config_keys=config_keys,
        default_config_key=default_config_key,
    )

    #
    func_apply_default = functools.partial(
        _apply_default_for_one_key, shared=shared)
    functools.update_wrapper(func_apply_default, _apply_default_for_one_key)
    func_apply_default.__name__ = 'apply_default'
    shared['func_apply_default'] = func_apply_default

    #
    ret = functools.partial(_expand_config, shared=shared)
    functools.update_wrapper(ret, _expand_config)
    ret.__name__ = 'expand_config'

    return ret

##__________________________________________________________________||
def _expand_config(cfg, shared=None):
    """expand a config into its full form

    Parameters
    ----------
    cfg : dict, None, or list of dicts and None
        Configuration

    shared : dict, optional

        To be given by ``config_expander()`` with
        ``functools.partial()``.

    Returns
    -------
    dict, list of dicts, or None
        Configuration in its full form

    """

    if cfg is None:
        return None

    if shared is None:
        shared = {}

    shared = copy.deepcopy(shared) # so successive calls don't share `shared`

    if is_dict(cfg):
        cfg = _expand_one_dict(cfg, shared)
        if not cfg:
            return None
        return cfg

    # cfg is a list of dicts and None

    ret = [ ]
    for c in cfg:
        if c is None:
            continue

        c = _expand_one_dict(c, shared)

        if c is None:
            continue

        if isinstance(c, list):
            c = [e for e in c if e is not None]
            ret.extend(c)
        else:
            ret.append(c)

    return ret

##__________________________________________________________________||
def _expand_one_dict(cfg, shared):
    """expand a piece of config

    Parameters
    ----------
    cfg : dict
        Configuration

    shared : dict
        A dict of shared objects

    Returns
    -------
    dict, list
        Expanded configuration

    """

    if shared['default_config_key'] is not None:
        if not (len(cfg) == 1 and list(cfg.keys())[0] in shared['config_keys']):
            cfg = {shared['default_config_key']: cfg}

    if not len(cfg) == 1:
        return cfg.copy()

    key, val = list(cfg.items())[0]

    if key not in shared['config_keys']:
        cfg = _apply_default_for_all_keys(cfg, shared)
        return cfg.copy()

    if key not in shared['expand_func_map']:
        cfg = _apply_default_for_all_keys(cfg, shared)
        return cfg.copy()

    expand_func = shared['expand_func_map'][key]
    try:
        return expand_func(val, shared)
    except TypeError:
        return expand_func(val)


##__________________________________________________________________||
def _set_default(cfg, shared):
    wrapped = _wrap_default_cfg(
        cfg, shared['config_keys'], shared['default_config_key'])
    shared['default_cfg_stack'].append(wrapped)
    return None

def _wrap_default_cfg(cfg, config_keys, default_config_key):
    if default_config_key is None:
        return cfg
    if set(cfg.keys()) <= set(config_keys):
        return cfg
    return {default_config_key: cfg}

##__________________________________________________________________||
def _apply_default_for_all_keys(cfg, shared):
    if 'default_cfg_stack' not in shared:
        return cfg
    ignore = ('set_default', )
    ret = {}
    for key, val in cfg.items():
        if key in ignore:
            ret[key] = val
            continue
        ret[key] = _apply_default_for_one_key(key, val, shared)
    return ret

def _apply_default_for_one_key(key, cfg, shared):
    """apply default to a config for a key

    Parameters
    ----------
    key : str
        A config key
    cfg : dict
        A config
    shared : dict
        A dict of shared objects.

    Returns
    -------
    function
        A config with default applied

    """

    ret = {}
    for default_cfg in shared['default_cfg_stack']:
        ret.update(default_cfg.get(key, {}))
    ret.update(cfg)
    return ret

##__________________________________________________________________||
