# encoding: utf-8
from __future__ import print_function, division, absolute_import


def template_variables(template):
    import re

    fields = re.findall("{[a-z_]+}", template)
    return [f.lstrip("{").rstrip("}") for f in fields]


def ask_values(variables, presets, input_=input):
    for field in variables:
        if field not in presets:
            while True:
                value = input_("{} = (.=exit) ? ".format(field)).strip()
                if value:
                    break
            if value == ".":
                yield None
            presets[field] = value
            yield field, value
        else:
            yield field, presets[field]
