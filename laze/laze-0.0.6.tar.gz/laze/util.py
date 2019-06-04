import hashlib
import json
import os
import traceback

# try to use libyaml (faster C-based yaml lib),
# fallback to pure python version
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print("laze: warning: using slow python-based yaml loader")
    from yaml import Loader, Dumper

from collections import defaultdict
from itertools import product, chain
from string import Template

def listify(something):
    """ if something is a list, return it.  else, return [something]."""

    if something is None:
        return []
    if not type(something) == list:
        return [something]
    return something


def uniquify(seq):
    """ make sure each member of seq is in there only once.

    order-reserving.
    """

    seen = set()
    return [x for x in seq if isinstance(x, dict) or (x not in seen and not seen.add(x))]


def print_exception():
    traceback.print_exc()


def dict_list_tuples2(_dict):
    for key, value_list in _dict.items():
        for value in value_list:
            yield (key, value)


def dict_list_tuples(_dict):
    _dict = _dict or {}
    for key in _dict.keys():
        yield dict_list_tuples2({key: _dict[key]})


def dict_list_product(_dict):
    for _tuple in product(*dict_list_tuples(_dict)):
        res = {}
        for key, val in _tuple:
            res[key] = val

        yield (res)


def deep_replace(obj, replace):
    if type(obj) == list:
        _obj = []
        for entry in obj:
            _obj.append(deep_replace(entry, replace))
        return _obj
    elif type(obj) == dict:
        _obj = {}
        for key, val in obj.items():
            _obj[key] = deep_replace(val, replace)
        return _obj
    elif type(obj) == str:
        for key, val in replace.items():
            obj = obj.replace(key, val)
        return obj
    else:
        return obj


def deep_substitute(_vars, _dict):
    """ for each key in vars, do Template substitution

    if value is a list, substitute each list member.
    """

    for k, v in _vars.items():
        if type(v) == list:
            for n, entry in enumerate(v):
                if "$" in entry:
                    v[n] = Template(entry).substitute(_dict)
        else:
            if "$" in v:
                _vars[k] = Template(v).substitute(_dict)

    return _vars

def deep_safe_substitute(_vars, _dict):
    """ for each key in vars, do Template substitution

    if value is a list, substitute each list member.
    """

    for k, v in _vars.items():
        if type(v) == list:
            for n, entry in enumerate(v):
                if "$" in entry:
                    v[n] = Template(entry).safe_substitute(_dict)
        else:
            if "$" in v:
                _vars[k] = Template(v).safe_substitute(_dict)

    return _vars


def merge(
    a,
    b,
    path=None,
    override=False,
    change_listorder=False,
    only_existing=False,
    join_lists=False,
):
    """merges b into a"""

    if path is None:
        path = []
    for key in b:
        if key in a:
            if join_lists:
                if isinstance(a[key], list) and not isinstance(b[key], list):
                    b[key] = [b[key]]
                elif (not isinstance(a[key], list)) and isinstance(b[key], list):
                    a[key] = [a[key]]

            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(
                    a[key],
                    b[key],
                    path=path + [str(key)],
                    override=override,
                    join_lists=join_lists,
                )
            elif isinstance(a[key], set) and isinstance(b[key], set):
                a[key] = a[key] | b[key]
            elif isinstance(a[key], list) and isinstance(b[key], list):
                if change_listorder:
                    a[key] = uniquify(b[key] + a[key])
                else:
                    a[key] = uniquify(a[key] + b[key])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif a[key] is None:
                a[key] = b[key]
            else:
                if override:
                    a[key] = b[key]
                else:
                    raise Exception(
                        "Conflict at %s (%s, %s)"
                        % (".".join(path + [str(key)]), a[key], b[key])
                    )
        else:
            if not only_existing:
                a[key] = b[key]
    return a


def flatten_var(var):
    removes = set()
    var_list = listify(var)
    prefixes = []
    suffixes = []
    for entry in var_list:
        if isinstance(entry, dict):
            remove_list = entry.get("remove")
            if remove_list:
                removes.update(listify(remove_list))
                continue

            prefix_list = entry.get("prefix")
            if prefix_list:
                prefixes.extend(prefix_list)
                continue

            suffix_list = entry.get("suffix")
            if suffix_list:
                suffixes.extend(suffix_list)
                continue

    return " ".join([x for x in chain(prefixes, var_list, suffixes) if not (isinstance(x, dict) or x in removes)])


def flatten_vars(vars):
    res = {}
    for name, _list in vars.items():
        res[name] = flatten_var(_list)
    return res


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


def split(_list, splitter=","):
    if len(_list) == 0:
        return []

    tmp = []
    for entry in _list:
        tmp.extend(entry.split(splitter))

    return tmp

def _dict_digest(_dict):
    return hashlib.sha1(json.dumps(_dict, sort_keys=True).encode("utf-8"))


def dict_digest(_dict):
    return _dict_digest(_dict).digest()


def dict_hexdigest(_dict):
    return _dict_digest(_dict).hexdigest()

def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d


def dump_dict(path, data):
    if type(path) == tuple:
        path = os.path.join(*path)
    path = path + ".yml"

    if type(data) == defaultdict:
        data = default_to_regular(data)

    with open(path, "w") as f:
        yaml.dump(data, f, Dumper=Dumper)

    return path


def load_dict(path):
    if type(path) == tuple:
        path = os.path.join(*path)
    path = path + ".yml"

    return yaml.load(open(path), Loader=Loader)
