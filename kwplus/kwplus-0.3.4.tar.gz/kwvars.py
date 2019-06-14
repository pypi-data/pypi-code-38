from itertools import product


class kwvars(list):
    pass


def separate_variations(kw):
    return ({k: v for k, v in kw.items()
             if isinstance(v, kwvars)},
            {k: v for k, v in kw.items()
             if not isinstance(v, kwvars)})


def config_vars_to_configs(**config_vars):
    if not config_vars:
        return [{}]
    config_keys, config_vals = zip(*config_vars.items())
    return [dict(zip(config_keys, vlist)) for vlist in product(*config_vals)]


def expand_variations(**kwargs):
    variations, common_kwargs = separate_variations(kwargs)
    expanded = config_vars_to_configs(**variations)
    return [dict(kw, **common_kwargs) for kw in expanded]
