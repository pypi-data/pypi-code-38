# -*- coding: utf-8 -*-
import re
import json
from .doc_parser import DocParser
from ..api_info import ApiInfo
from .. import debug, info, warn, error


class CliDoc(DocParser):
    """
    用于生成需要的对接数据结构
    """

    @classmethod
    def parse_doc(cls, the_doc_lines):
        # debug("对doc生成路由信息 {doc}".format(doc='\n'.join(the_doc_lines)))
        route_info = {'params': [], 'example': [], 'raw_example': [], 'response': []}
        route_match_regexp = {
            'api': r'\s*@api\s+(.*)\s*$',
            'name': r'\s*@name\s+(.*)\s*$',
            'description': r'\s*@description\s+(.*)\s*$',
            'author': r'\s*@author\s+(.*)\s*$',
            'params': r'\s*@params\s*$',
            'example': r'\s*@example[s]*\s*$',
            'raw_example': r'\s*@raw_example[s]*\s*$',
            'response': r'\s*@response\s+(.*)\s*$',
            'expect': r'\s*@expect\s+(.*)\s*$',
            'toolable': r'\s*@toolable\s*(.*)\s*$',
            'long_description': r'\s*@long_description\s*$',
        }
        is_get_params = False
        is_get_example = False
        is_get_raw_example = False
        is_long_description = False
        for one_line in the_doc_lines:
            if is_get_params:
                if one_line.find('name:') != -1 and one_line.find('type:') != -1 and one_line.find('desc:') != -1:
                    debug("这是一个参数行:{}".format(one_line))
                    route_info['params'].append(cls.parse_att_params(one_line))
                else:
                    debug("这已经不是一个参数行:{}".format(one_line))
                    is_get_params = False
            if is_get_example:
                if one_line.find('usage:') != -1 and one_line.find('desc:') != -1:
                    debug("这是一个例子行:{}".format(one_line))
                    route_info['example'].append(cls.parse_att_example(one_line))
                else:
                    debug("这已经不是一个例子行:{}".format(one_line))
                    is_get_example = False
            if is_long_description:
                if re.match("^\s*@", one_line):
                    debug("这已经不是一个 long_description {}".format(one_line))
                    is_long_description = False
                else:
                    route_info['long_description'] = '\n'.join([route_info['long_description'], one_line])

            if is_get_raw_example:
                if re.match("^\s*@", one_line):
                    debug("这已经不是一个 raw_example {}".format(one_line))
                    is_get_raw_example = False
                else:
                    route_info['long_description'] = '\n'.join([route_info['long_description'], one_line])

            for one_key in route_match_regexp.keys():
                match_data = re.match(route_match_regexp[one_key], one_line)
                if match_data:
                    if one_key == 'params':
                        is_get_params = True
                        continue
                    if one_key == 'example':
                        is_get_example = True
                        continue
                    if one_key == 'api':
                        api_match_split = re.split(r'\s+', match_data.group(1))
                        if len(api_match_split) == 1:
                            route_info['url'] = api_match_split[0]
                        elif len(api_match_split) == 2:
                            route_info['method'] = re.split(r'\s+', match_data.group(1))[0]
                            route_info['url'] = re.split(r'\s+', match_data.group(1))[1]
                        else:
                            error("api行写的不对,只能有两个参数:{}".format(one_line))
                        continue
                    if one_key == 'raw_example':
                        is_get_raw_example = True
                        continue
                    if one_key == 'long_description':
                        is_long_description = True
                        route_info[one_key] = ''
                        continue
                    if one_key == 'toolable':
                        route_info[one_key] = 'true'
                        continue
                    route_info[one_key] = match_data.group(1).strip()
        debug('最后得到的一个路由信息是:{}'.format(json.dumps(route_info)))
        if route_info.get('name', None) is None:
            info("无法解析到name,认为这个解析是失败的")
            return None
        api_info = ApiInfo(route_info)
        return api_info

    @classmethod
    def parse_att_params(cls, params_line):
        desc_arr = params_line.split('desc:')
        the_desc = desc_arr.pop().strip()
        params_arr = desc_arr[0].split(',')
        param_info = {'id': params_arr[0].strip(), 'desc': the_desc}
        for one_param_opt_str in params_arr[1:]:
            debug("需要处理 {}".format(one_param_opt_str))
            one_param_opt_str = one_param_opt_str.strip()
            if len(one_param_opt_str) == 0:
                debug('有","分割的空行,容错处理 {}'.format(one_param_opt_str))
                continue
            param_opt_arr = one_param_opt_str.split(':')
            if len(param_opt_arr) != 2:
                debug('没有":"的一个参数项,容错处理 {}'.format(params_arr))
                continue
            param_key = param_opt_arr[0].strip()
            param_value = param_opt_arr[1].strip()
            param_info[param_key] = param_value
        debug("获取到的参数解析信息:{}".format(json.dumps(param_info)))
        return param_info

    @classmethod
    def parse_att_example(cls, params_line):
        desc_arr = params_line.split('desc:')
        the_desc = desc_arr.pop().strip()
        params_arr = desc_arr[0].split('usage:')
        param_info = {
            'desc': the_desc,
            'usage': params_arr.pop().strip()
        }
        debug("获取到的example解析信息:{}".format(json.dumps(param_info)))
        return param_info
