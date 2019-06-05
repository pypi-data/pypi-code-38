# -*- coding: utf-8 -*-
import io
import json
import logging

import jinja2
import yaml

logger = logging.getLogger(__name__)

try:
    # noinspection PyPep8Naming
    import ConfigParser as configparser
except ImportError:
    # noinspection PyUnresolvedReferences
    import configparser


__Expected_sections = ['Inputs', 'Outputs', 'Parameters']
__NULL = '!!NULL!!'


def get_declared_variables(file_path):
    state = 'scan'
    declares = {}
    line_count = 0
    with open(file_path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            line_count += 1
            if line.startswith('[DECLARE]'):
                state = 'start'
                continue
            elif line.strip().startswith(";"):
                continue
            elif line.startswith('['):
                break
            if state == 'start' and line.strip():
                declares[line] = line_count

    variables = []
    for declare in declares:
        seg = declare.split("=", 1)
        if len(seg) != 2:
            raise ValueError('Illegal declare in the config file in the line: {}'.format(declares[declare]))
        variable_name = seg[1].strip()
        if variable_name[:2] != "{{" or variable_name[-2:] != "}}":
            raise ValueError('Illegal variable name: {}, line: {}'.format(variable_name, declares[declare]))
        variables.append(variable_name[2:-2])
    return variables


def get_rendered_config(config_path, var_map):
    """

    :param config_path: 参数ini配置文件
    :param var_map: 变量名与值的映射
    :type var_map: function
    :rtype: ConfigParser.ConfigParser
    """
    with open(config_path, 'r') as f:
        template = jinja2.Template(f.read())

    var_names = get_declared_variables(config_path)

    def mapper(item):
        v = var_map(item)
        return __NULL if v is None else v

    kv = {v_name: mapper(v_name) for v_name in var_names}
    rendered = template.render(**kv)
    parser = configparser.ConfigParser()
    # 区分大小写
    parser.optionxform = str

    fp = io.StringIO(rendered)
    # Use 'parser.read_file()' instead in py3
    parser.readfp(fp)
    return parser


def fill_parameter_yml_template(config_path, var_map, template_file, target_output):
    """

    :param config_path: 参数ini配置文件
    :param var_map: 变量名与值的映射
    :type var_map: function
    :param template_file: 空参数模板yml
    :param target_output: 输出路径
    :return:
    """

    with open(template_file, 'r') as f:
        parameter_dict = yaml.load(f, Loader=yaml.SafeLoader)
    parser = get_rendered_config(config_path, var_map)

    def fill_sections(section, direct=False):
        if not parser.has_section(section):
            return

        target = parameter_dict if direct else parameter_dict[section]

        for key, value in parser.items(section):
            _fill_value(key, value, target)

    fill_sections('!DIRECT', True)
    for s in __Expected_sections:
        fill_sections(s)

    with open(target_output, 'w') as f:
        yaml.dump(parameter_dict, f, Dumper=yaml.SafeDumper, allow_unicode=True)


def _fill_value(key, value, target):
    """

    :param key:
    :param value:
    :type target: dict
    :return:
    """
    if not key:
        raise ValueError("`Key` must be not null")
    entity = target
    seg_list = key.split('.')

    for pos in seg_list[:-1]:
        if not pos:
            raise ValueError('Illegal key: {}'.format(key))
        if pos.startswith('$'):
            # $0 => 指定数组，若出错，则说明配置有问题
            entity = entity[int(pos[1:])]
        else:
            entity = entity[pos]

    if (value and value[0] == value[-1] == '\"') or (entity.get('type') and entity['type'] not in ['string']):
        # 消除ini文件中的value的双引号, 将bool、integer等值转为正确的类型
        try:
            value = json.loads(value)
        except ValueError as e:
            logger.info("Reload type of value failed. %s: %s", key, e)

    if value == __NULL:
        value = None

    entity[seg_list[-1]] = value
