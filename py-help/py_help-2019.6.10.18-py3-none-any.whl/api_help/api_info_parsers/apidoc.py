# -*- coding: utf-8 -*-
import re
import json
from .doc_parser import DocParser
from ..api_info import ApiInfo
from .. import debug, info, warn, error

apidoc_match_dict = {
    'api': r'\s*@api\s+(.*)\s*$',
    'name': r'\s*@apiName\s+(.*)\s*$',
    'group': r'\s*@apiGroup\s+(.*)\s*$',
    'version': r'\s*@apiVersion\s+(.*)\s*$',
    'permission': r'\s*@apiPermission\s+(.*)\s*$',
    'deprecated': r'\s*@apiDeprecated\s+(.*)\s*$',
    'description': r'\s*@apiDescription\s+(.*)\s*$',
    'header': r'\s*@apiHeader\s+(.*)\s*$',
    'author': r'\s*@author\s+(.*)\s*$',
    'params': r'\s*@apiParam\s+(.*)\s*$',
    'params_example': r'\s*@apiParamExample\s*$',
    'success_ret': r'\s*@apiSuccess\s+(.*)\s*$',
    'success_example': r'\s*@apiSuccessExample\s+(.*)\s*$',
    'error_ret': r'\s*@apiError\s+(.*)\s*$',
    'error_example': r'\s*@apiErrorExample\s+(.*)\s*$',
    'use_define': r'\s*@apiUse\s*$',
    'define': r'\s*@apiDefine\s*$',
    'example': r'\s*@apiExample\s+(.*)\s*$',
    'header_example': r'\s*@apiHeaderExample\s+(.*)\s*$',
    'toolable': r'\s*@apiPrivate\s*(.*)\s*$',
}


class ApiDoc(DocParser):
    """
    用于生成需要的对接数据结构
    """

    @classmethod
    def parse_doc(cls, the_doc_lines):
        # debug("对doc生成路由信息 {doc}".format(doc='\n'.join(the_doc_lines)))
        api_info = {'params': [], 'example': [], 'raw_example': [], 'response': []}
        multi_line_check_mark_dict = {
            'multi_line_check': False,
        }
        for one_line in the_doc_lines:
            cls.check_in_multi_line(one_line, multi_line_check_mark_dict, api_info)

            cls.check_match_key(one_line, multi_line_check_mark_dict, api_info)
        debug('最后得到的一个路由信息是:{}'.format(json.dumps(api_info, indent=2)))
        if api_info.get('name', None) is None:
            warn("无法解析到name,认为这个解析是失败的")
            return None
        api_info = ApiInfo(api_info)
        return api_info

    @classmethod
    def check_match_key(cls, one_line, multi_line_check_mark_dict, api_info):
        for one_key in apidoc_match_dict.keys():
            match_data = re.match(apidoc_match_dict[one_key], one_line)
            if match_data:
                if one_key == 'api':
                    api_str_arr = re.split('\s+', match_data.group(1))
                    if "{" in api_str_arr[0] and "}" in api_str_arr[0]:
                        api_info['method'] = re.sub('\{|\}', "", api_str_arr[0]).lower()
                        api_info['url'] = api_str_arr[1]
                        api_info['title'] = ''.join(api_str_arr[2::])
                    else:
                        error("API获取出错:{}".format(api_str_arr))
                    continue
                if one_key == 'error_ret':
                    if api_info.get('error_ret') is None:
                        api_info['error_ret'] = {}
                    error_ret_info = api_info.get('error_ret')
                    cls.setup_error_ret(error_ret_info, match_data)
                    continue
                if one_key in ['params_example', 'success_example', 'error_example', 'example', 'header_example']:
                    multi_line_check_mark_dict['multi_line_check'] = one_key
                    api_info[one_key] = ''
                    continue
                if one_key == 'params':
                    cls.parse_params(api_info, match_data)
                    continue
                api_info[one_key] = match_data.group(1).strip()

    @classmethod
    def setup_error_ret(cls, error_ret_info, match_data):
        ret_data_arr = re.split("\s+", match_data.group(1))
        group_id = '400'
        field_name = ''
        field_type = ''
        field_desc = ''
        if len(ret_data_arr) > 2:
            if "(" in ret_data_arr[0] and ")" in ret_data_arr[0]:
                group_id = re.sub('\(|\)', "", ret_data_arr[0])
                if "{" in ret_data_arr[1] and "}" in ret_data_arr[1]:
                    field_type = re.sub('\{|\}', "", ret_data_arr[1])
                    field_name = ret_data_arr[2]
                    field_desc = ' '.join(ret_data_arr[3::])
                else:
                    field_name = ret_data_arr[1]
                    field_desc = ' '.join(ret_data_arr[2::])
            elif "{" in ret_data_arr[0] and "}" in ret_data_arr[0]:
                field_type = re.sub('\{|\}', "", ret_data_arr[0])
                field_name = ret_data_arr[1]
                field_desc = ' '.join(ret_data_arr[2::])
            else:
                field_name = ret_data_arr[0]
                field_desc = ' '.join(ret_data_arr[1::])
        else:
            field_name = ret_data_arr[0]
        if error_ret_info.get(group_id) is None:
            error_ret_info[group_id] = {}
        err_ret_group = error_ret_info.get(group_id)
        err_ret_group[field_name] = {
            'desc': field_desc,
            'type': field_type,
        }

    @classmethod
    def check_in_multi_line(cls, one_line, multi_line_check_mark_dict, api_info):
        multi_line_type = multi_line_check_mark_dict['multi_line_check']
        if multi_line_type:
            if re.match('^\s*@api', one_line):
                debug("already match other :{}".format(one_line))
                multi_line_check_mark_dict['multi_line_check'] = False
                return
            api_info[multi_line_type] += one_line + "\n"

    @classmethod
    def parse_params(cls, api_info, match_data):
        if api_info.get('params') is None:
            api_info['params'] = []
        param_info = api_info.get('params')
        debug("匹配的参数字符串:{}".format(match_data.group(1)))
        param_arr = re.split("\s+", match_data.group(1))
        param_info_dict = {
            'id': 'unknwon_id',
            'type': 's',
            'group': 'Parameter',
            'desc': 'unknown desc',
        }
        if "(" in param_arr[0] and ")" in param_arr[0]:
            param_info_dict['group'] = re.sub('\(|\)', "", param_arr[0])
            if "{" in param_arr[1] and "}" in param_arr[1]:
                cls.parse_params_type(param_info_dict, param_arr[1])
                cls.parse_params_name(param_info_dict, param_arr[2])
                param_info_dict['desc'] = ''.join(param_arr[3::])
            else:
                cls.parse_params_name(param_info_dict, param_arr[1])
        else:
            # 没有分组
            if "{" in param_arr[0] and "}" in param_arr[0]:
                cls.parse_params_type(param_info_dict, param_arr[0])
                cls.parse_params_name(param_info_dict, param_arr[1])
                param_info_dict['desc'] = ''.join(param_arr[2::])
            else:
                cls.parse_params_name(param_info_dict, param_arr[1])
                param_info_dict['desc'] = ''.join(param_arr[2::])
        param_info.append(param_info_dict)
        return param_info

    @classmethod
    def parse_params_type(cls, param_info_dict, type_str):
        debug("开始解析参数type :{}".format(type_str))
        # 这里就是内部有中括号,表达类型有限制性条件
        the_match = re.match('{.*{(\S*)}.*}', type_str)
        if the_match:
            valid_str = the_match.group(1)
            debug("存在限制条件:{}".format(valid_str))
            if '..' in valid_str:
                param_info_dict['length'] = valid_str
            elif '-' in valid_str:
                param_info_dict['range'] = valid_str
            else:
                warn("限制字符串:{}貌似不支持".format(valid_str))
            type_str = re.sub(valid_str, '', type_str)
        else:
            debug("没有限制条件:{}".format(type_str))
        type_str = re.sub('\{|\}', "", type_str)
        if '=' in type_str:
            debug("存在选项:{}".format(type_str))
            type_arr = type_str.split('=')
            param_info_dict['type'] = type_arr[0].strip().lower()
            param_info_dict['values'] = type_arr[1].strip()
        else:
            param_info_dict['type'] = type_str.strip().lower()

    @classmethod
    def parse_params_name(cls, param_info_dict, name_str):
        debug("开始解析参数名字 :{}".format(name_str))
        if "[" in name_str and "]" in name_str:
            param_info_dict['required'] = 'false'
            name_str = re.sub('\[|\]', "", name_str)
        else:
            param_info_dict['required'] = 'true'
        debug("api的参数字符串是:{}".format(name_str))
        name_arr = name_str.split('=')
        param_info_dict['name'] = name_arr[0]
        param_info_dict['id'] = name_arr[0]
        if len(name_arr) > 1:
            param_info_dict['default'] = ''.join(name_arr[1::])

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
