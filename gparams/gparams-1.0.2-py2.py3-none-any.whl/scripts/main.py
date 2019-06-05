# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import json

from gparams import yml2ini
from gparams import ini2yml

from gparams.__about__ import VERSION


def _load_variable(arguments):
    print("ignore the keys with suffix(s):", arguments.ignore)
    yml2ini.params_reduction(
        param_path=arguments.yml,
        ignore_list=arguments.ignore,
        is_template=arguments.is_template
    )


def _detection_variable(arguments):
    _values = json.loads(arguments.values) if arguments.values else {}
    yml2ini.detection(arguments.file, _values)


def _map(arguments):
    _values = json.loads(arguments.values) if arguments.values else {}
    var_mapper = ini2yml.dict_to_mapper(_values)
    ini2yml.generate_param_yml(
        ini_path=arguments.ini,
        empty_yml_path=arguments.yml,
        output=arguments.output,
        var_mapper=var_mapper
    )


def main():
    parser = argparse.ArgumentParser(description="参数变量提取工具，用于将yml参数文件中的变量提取到ini配置模板中")
    sub_parsers = parser.add_subparsers()

    version = sub_parsers.add_parser("version", description="print version")
    version.set_defaults(func=lambda x: print(VERSION))

    # 导出主要变量
    parser_load = sub_parsers.add_parser("load", description="load the variables from yml file")
    parser_load.set_defaults(func=_load_variable)

    parser_load.add_argument('-y', '--yml', required=True, help="parameter file path")
    parser_load.add_argument('-i', '--ignore',
                             nargs='+',
                             help='ignore the giving parameters (suffix)'
                             )
    parser_load.add_argument('-t', '--is-template',
                             dest="is_template",
                             action='store_true',
                             help='is template parameter file (include the placeholders)'
                             )

    # 检查ini配置模板
    parser_detection = sub_parsers.add_parser("detection", description="render the variables and print")
    parser_detection.set_defaults(func=_detection_variable)
    parser_detection.add_argument("-f", '--file', required=True, help="template file")
    parser_detection.add_argument("-v", '--values', dest='values',
                                  help="giving the variables (json) to render the template")

    # 通过配置文件生成yml参数文件
    yml_mapper = sub_parsers.add_parser(
        "map",
        description="render the variables and generate to workflow parameters file (yml)"
    )
    yml_mapper.set_defaults(func=_map)
    yml_mapper.add_argument(
        "-i", "--ini", help="ini config of variables",
        dest="ini",
        required=True
    )
    yml_mapper.add_argument(
        "-y", "--yml", help="(empty) workflow parameters template file",
        dest="yml",
        required=True
    )
    yml_mapper.add_argument(
        "-v", "--values", help="the variables to render (input as json)",
        dest="values",
        required=False,
    )
    yml_mapper.add_argument(
        "-o", "--output", help="the path of parameter file to output",
        dest="output",
        required=False,
        default="output.yml"
    )

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
