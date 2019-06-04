# -*- coding: utf-8 -*-

from . import parameters


def generate_param_yml(ini_path, empty_yml_path, var_mapper, output):

    parameters.fill_parameter_yml_template(
        config_path=ini_path,
        template_file=empty_yml_path,
        target_output=output,
        var_map=var_mapper
    )


def dict_to_mapper(value_dict):

    def mapper(item):
        if not value_dict:
            return None
        return value_dict.get(item)

    return mapper
