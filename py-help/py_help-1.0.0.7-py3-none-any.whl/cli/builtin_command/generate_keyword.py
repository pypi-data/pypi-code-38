# -*- coding: utf-8 -*-
import sys
import os
from prettytable import PrettyTable
from ..router import router
from .. import debug, info, warn, error
from py_help.api_help.api_wrapper import Api
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


def generate_custom_param_xml(xml_node):
    one_param_node = ET.SubElement(xml_node, 'param')
    one_param_node.set('id', '_device')
    one_param_node.set('name', '_运行目标')
    one_param_node.set('type', 's')
    one_param_node.set('desc', '指定运行的测试设备')
    one_param_node = ET.SubElement(xml_node, 'param')
    one_param_node.set('id', '_return')
    one_param_node.set('name', '_返回值类型')
    one_param_node.set('type', 'b')
    one_param_node.set('default', 'false')
    one_param_node.set('values', 'true|false')
    one_param_node.set('desc', '特殊参数,表示关键字是返回值还是返回成功失败')
    one_param_node = ET.SubElement(xml_node, 'param')
    one_param_node.set('id', '_exception_retry')
    one_param_node.set('name', '_重试次数')
    one_param_node.set('type', 'i')
    one_param_node.set('default', '0')
    one_param_node.set('desc', '特殊参数,通过SSH通道的异常重试')
    one_param_node = ET.SubElement(xml_node, 'param')
    one_param_node.set('id', '_max_timeout')
    one_param_node.set('type', 'i')
    one_param_node.set('name', '_最大超时时间')
    one_param_node.set('default', '300')
    one_param_node.set('desc', '特殊参数,通过SSH通道的最大超时时间')
    one_param_node = ET.SubElement(xml_node, 'param')
    one_param_node.set('id', '_backend')
    one_param_node.set('name', '_后台运行')
    one_param_node.set('type', 's')
    one_param_node.set('values', 'y|n')
    one_param_node.set('desc', '后台运行相关命令,默认都是前台运行,只有配置了此参数,才会后台运行')


def generate_node_xml(xml_node, node_name, node_dict, run_type, name_prefix):
    the_rule = node_dict.get('rule', None)
    the_route_info = node_dict.get('route_info')
    debug("需要生成 node:{}".format(the_rule))
    if the_rule is None or the_route_info is None:
        error("出现异常,没有rule或者route_info的节点:{},{}".format(node_name, the_rule))
    else:
        the_name_space = '::'.join(the_rule.split('/'))
        the_node = ET.SubElement(xml_node, 'keyword')
        the_node.set('id', name_prefix + node_name)
        the_node.set('namespace', the_name_space)
        the_node.set('name', name_prefix + the_route_info.get('name', 'Unknown'))
        the_node.set('cmd', '{app} {url}'.format(app=sys.argv[0], url=' '.join(the_rule.split('/'))))
        run_type_match = {
            'ssh': 'AtkKeywordProxy::Ssh::Client|exec_command'
        }
        the_node.set('handler', run_type_match.get(run_type))
        the_node.set('author', the_route_info.get('author', '未知作者'))
        if the_route_info.get('long_description') is not None:
            the_node.set('long_description', the_route_info.get('long_description'))
        the_node.set('description', the_route_info.get('description', '这家伙没有写描述'))
        the_node.set('toolable', the_route_info.get('toolable', 'false'))
        the_params = the_route_info.get('params')
        params_node = ET.SubElement(the_node, 'params')
        if the_params is None:
            warn("出现没有参数的keyword:{}".format(the_rule))
        else:
            debug("处理参数组:{}".format(the_params))
            for one_param in the_params:
                one_param_node = ET.SubElement(params_node, 'param')
                for (k, v) in one_param.items():
                    one_param_node.set(k, v)
        generate_custom_param_xml(params_node)
        expect_node = ET.SubElement(the_node, 'expect')
        expect_str = the_route_info.get('expect', '成功|失败|NONE')
        debug("生成expect:{}".format(expect_str))
        expect_node.text = expect_str
    return True


def generate_group_xml(xml_node, group_name, group_dict, run_type, name_prefix):
    debug("开始生成分组:{}".format(group_name))
    group_node = ET.SubElement(xml_node, 'namespace')
    group_node.set('id', group_name)
    group_node.set('name', group_name)
    group_node.set('description', group_name)
    group_node.set('cmd', '')
    node = group_dict.get('node', None)
    if node is not None:
        generate_node_xml(xml_node, group_name, node, run_type, name_prefix)
    for (k, v) in group_dict.get('child').items():
        if v.get('type') == 'group':
            generate_group_xml(group_node, k, v, run_type, name_prefix)
        else:
            generate_node_xml(group_node, k, v.get('node'), run_type, name_prefix)


def generate_xml(run_type, out_path, name_prefix):
    root = ET.Element('att_python')
    name_space = ET.SubElement(root, 'namespace')
    the_name = 'att_python_{}'.format(run_type)
    name_space.set('id', the_name)
    name_space.set('name', the_name)
    name_space.set('description', 'python项目对接att的相关')
    for (k, v) in router.route_group_table.get('child').items():
        if v.get('type') == 'group':
            generate_group_xml(name_space, k, v, run_type, name_prefix)
        else:
            generate_node_xml(name_space, k, v.get('node'), run_type, name_prefix)

    debug('生成的xml是:{}'.format(root))
    rough_string = ET.tostring(root, 'utf-8', 'xml')
    debug('生成的xml是:{}'.format(rough_string))
    reared_content = minidom.parseString(rough_string)
    with open(out_path, 'w+') as fs:
        reared_content.writexml(fs, addindent=" ", newl="\n", encoding="utf-8")


@Api()
def generate_keyword(**kwargs):
    """
    @api /py/generate/keyword
    @name 生成keyword信息
    @toolable
    @description 生成对接自动化平台的keyword信息
    @author 王沃伦
    @params
        run_type,name:运行类型,type:s,required:true,values:ssh|xml_rpc|cmd,default:ssh,desc:通过什么方式运行,ssh就是要ssh到服务器上跑,xml_rpc就是本地用xml_rpc来跑,cmd是翻译成本地cmd
        type,name:信息类型,type:s,required:true,values:xml|json,default:xml,desc:生成的信息类型,默认都是xml
        name_prefix,name:名称前缀,type:s,required:false,default:,desc:生成的关键字名字的前缀,默认为空,也就是注释里面是什么就是什么,添加了前缀后可以避免命名冲突
        out_path,name:输出路径,type:s,required:true,default:./,desc:生成的文件存放路径
    @example
        usage:py generate keyword --run_type=ssh,desc:生成ssh形式运行的xml的keyword信息
    @expect 成功|失败|NONE
    """
    the_run_type = kwargs.get('run_type', 'ssh')
    the_data_type = kwargs.get('type', 'xml')
    the_out_path = kwargs.get('out_path', './')
    name_prefix = kwargs.get('name_prefix', '')
    debug("生成keyword信息-the_run_type:{}".format(the_run_type))
    generate_hash = {
        'xml': generate_xml
    }
    out_real_path = os.path.realpath(os.path.join(the_out_path, 'out_keyword.{}'.format(the_data_type)))
    generate_handler = generate_hash.get(the_data_type, None)
    if generate_handler is None:
        msg = "不支持{}信息类型".format(the_data_type)
        error(msg)
        return router.fail_msg(msg)
    else:
        return generate_handler(the_run_type, out_real_path, name_prefix)
