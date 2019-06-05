#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import json
import os

import jinja2
import yaml


def _template_to_readable_yml(param_path):
    """模板yml文件中包含花括号等占位符，无法直接读取，需要添加引号使它可读
    :return: 返回临时的文件地址
    """
    lines = []
    with open(param_path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            sp = line.split(":", 1)
            if len(sp) != 2:
                lines.append(line)
                continue
            value = sp[1].strip()
            if "{" in value and not (value.startswith("\"") or value.startswith("\'")):
                value = "\"{}\"".format(value)
            line = ": ".join([sp[0], value])
            lines.append(line)

    temp = param_path + ".format.tmp.yml"
    with open(temp, 'w') as f:
        f.write("\n".join(lines))
    return temp


def params_reduction(param_path, ignore_list=None, is_template=False):
    ignore_list = ignore_list or []

    file_name = os.path.basename(param_path)

    def callback():
        pass

    if is_template:
        param_path = _template_to_readable_yml(param_path)

        def delete_tmp():
            if os.path.exists(param_path):
                os.remove(param_path)
        callback = delete_tmp

    with open(param_path, 'r') as f:
        template = yaml.load(f)

    default_value = {}

    inputs = template['Inputs']
    input_var_list = []

    def get_data(key, content, section='inputs'):
        if content.get('data'):
            try:
                assert isinstance(content['data'], list)
            except AssertionError:
                if "{" in content['data']:
                    print("TEMPLATE:", key, ":", content['data'])
                    return
                else:
                    print(key, content['data'])
                    raise
            var_name = '.'.join([key, 'data', '$0', 'name'])
            var_default_value = content['data'][0]['name']
            yield var_name, var_default_value
        elif content.get(section):
            for sub in content[section]:
                for var_name, var_default_value in get_data(sub, content[section][sub]):
                    yield '.'.join([key, section, var_name]), var_default_value

    for k, v in inputs.items():
        for name, value in get_data(k, v):
            default_value[name] = value
            input_var_list.append(name)
    input_var_list.sort()

    outputs = template['Outputs']
    output_var_list = []
    for k, v in outputs.items():
        for name, value in get_data(k, v, 'outputs'):
            default_value[name] = value
            output_var_list.append(name)
    output_var_list.sort()

    parameter_var_list = []
    parameters = template['Parameters']
    for k, v in parameters.items():

        try:
            assert isinstance(v['parameters'], dict)
        except AssertionError:
            if "{" in v['parameters']:
                print("TEMPLATE:", k, ":", v['parameters'])
                continue
            else:
                raise
        for p_name, p_info in v['parameters'].items():
            name = '.'.join([k, 'parameters', p_name, 'value'])
            default_value[name] = p_info['value']
            parameter_var_list.append(name)
    parameter_var_list.sort()

    with open('{}.param.ini'.format(file_name), 'w') as f:
        def write_line(section, key):
            for ignore in ignore_list:
                if key.endswith(ignore):
                    print("IGNORED:", key, " SECTION:", section)
                    return
            d_value = json.dumps(default_value[key])
            line = "{} = {}\n".format(key, d_value)
            f.write(line)

        f.write(";The variables of template file: {} \n".format(file_name))

        f.write(
            "\n[DECLARE]\n"
            ";Declare your variables here\n"
            "\n[MACROS]\n"
            ";Define Jinja macros here\n"
            "\n[!DIRECT]\n"
            ";Specify the parameters of the first layer here\n"
        )

        f.write("\n[Inputs]\n")
        for item in input_var_list:
            write_line('Inputs', item)

        f.write("\n[Outputs]\n")
        for item in output_var_list:
            write_line('Outputs', item)

        f.write("\n[Parameters]\n")
        for item in parameter_var_list:
            write_line('Parameters', item)
    callback()


def detection(template_file, values):
    """

    :param template_file: 模板文件路径
    :param values: 键值对(dict)
    """

    values = values or {}
    with open(template_file, 'r') as f:
        template = jinja2.Template(f.read())

    rendered = template.render(**values)
    print(rendered)
