import yaml
import os

def update(d, ud):
    for key, value in ud.items():
        overwrite = False
        if key.endswith('!'):
            key = key[:-1]
            overwrite = True
        if key not in d:
            d[key] = value
        elif isinstance(value, dict):
            if overwrite:
                d[key] = value
            else:
                update(d[key], value)
        elif isinstance(value, list) and isinstance(d[key], list):
            if overwrite:
                d[key] = value
            else:
                d[key] += value
        elif overwrite:
            d[key] = value

def load_include(value, include_path):
    path = os.path.abspath(os.path.join(os.path.dirname(include_path[-1]), value))
    if path in include_path:
        raise ValueError("Recursive import of {} (path: {})"\
            .format(path, '->'\
            .join(['"{}"'\
            .format(s) for s in include_path])))
    return load_config(path, include_path=include_path+[path])

def load_includes(config, include_path):
    if isinstance(config, dict):

        d = config.copy()

        for key, value in d.items():
            d[key] = load_includes(value, include_path=include_path)

        if '$include' in d:

            if d.get('$as-list'):
                nds = []
                is_list = True
            else:
                is_list = False
                nds = d.copy()
                del nds['$include']

            includes = d['$include']

            if not isinstance(includes, list):
                includes = [includes]
            for include in includes:
                nd = load_include(include, include_path)
                if nd is None:
                    continue
                if is_list:
                    if not isinstance(nd, (list, tuple)):
                        raise ValueError("expected a list or tuple")
                    nds.extend(nd)
                else:
                    if not isinstance(nd, dict):
                        raise ValueError("expected a dictionary")
                    update(nds, nd)
            return nds
        return d
    elif isinstance(config, (list, tuple)):
        l = []
        for c in config:
            result = load_includes(c, include_path=include_path)
            if isinstance(c, dict) and '$include' in c and isinstance(result, list):
                l.extend(result)
            else:
                l.append(result)
        return l
    return config
            

def load_config(filename, include_path=None):
    if include_path is None:
        include_path = [os.path.abspath(filename)]
    with open(filename) as input_file:
        config = yaml.load(input_file.read())
    return load_includes(config, include_path=include_path)
