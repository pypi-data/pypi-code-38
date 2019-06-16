# -*- coding: utf-8 -*-
from prettytable import PrettyTable
from ..router import router
from py_help.api_help.api_wrapper import Api
import sys
from .. import debug, info, warn, error


def print_one_command_help(the_url, the_route):
    route_info = the_route.get('route_info')
    if route_info is None or route_info.get('name', None) is None:
        print("===========这家伙没有按标准写帮助,帮助乱写的============")
        print(the_route.get('handler').__doc__)
    else:
        debug("需要用路由信息打印帮助:{url}::{r}".format(url=the_url, r=route_info))
        print('NAME\n')
        print('\t{key} - {name}\n'.format(key=' '.join(the_url.split('/')), name=route_info.get('name', None)))
        # print('\n')
        print('SYNOPSIS\n')
        print('\t{entr} {url} [options]\n'.format(entr=sys.argv[0], url=' '.join(the_url.split('/'))))
        # print('\n')
        print('DESCRIPTION\n')
        print('\t{desc}\n'.format(desc=route_info.get('description', '这货居然没写描述~!')))
        long_description = route_info.get('long_description')
        if long_description is not None:
            print(long_description)
        # print('\n')
        print('OPTIONS\n')
        the_params = route_info.get('params', [])
        for one_param in the_params:
            print('\t--{key}=arg    \t{desc}(default:{default})[select:{values}]\n'.format(
                key=one_param.get('id', 'Unknown'), desc=one_param.get('desc', '这货居然没写描述~!'),
                default=one_param.get('default', 'No default'), values=one_param.get('values', 'No select value')))
        # print('\n')
        print('EXAMPLES\n')
        the_examples = route_info.get('example', [])
        if len(the_examples) == 0:
            print('\t我了个大X,这货居然一个帮助示例都没写\n')
        else:
            for one_example in the_examples:
                print('\t#{desc}\n'.format(desc=one_example.get('desc', '这货居然没写描述~!')))
                print('\t{app} {usage}\n'.format(app=sys.argv[0], usage=one_example.get('usage', '这货居然没用法~!')))
        print('Author\n')
        print('\t{author}'.format(author=route_info.get('author')))


def show_url_list(url_list):
    url_list = sorted(url_list)
    list_table = PrettyTable(["命令路由", "命令名字", "简要描述", "作者/维护人"])
    list_table.align["命令路由"] = "l"
    list_table.padding_width = 1
    for one_url in url_list:
        the_route = router.match_rule(one_url)
        show_url = ' '.join(one_url.split('/'))
        the_route_info = the_route.get('route_info')
        if the_route_info is None:
            list_table.add_row([show_url, '这货没有按标准写帮助', '这货没有按标准写帮助', '这货没有按标准写帮助'])
        else:
            list_table.add_row(
                [show_url, the_route_info.get('name', None), the_route_info.get('description', '这货居然没写描述~!'),
                 the_route_info.get('author', None)])
    return str(list_table)


@Api(url='help', public=True, is_cli=True, router=router)
def help_command(**kwargs):
    """
    @name 输出帮助
    @toolable
    @description 为所有的命令入口打印相关的帮助
    @author 王沃伦
    @params
        url,name:命令url,type:s,required:true,default:/,desc:需要帮助的命令url,当是/的时候,就是列出所有的命令
    @example
        usage:help test,desc:列出命令test的帮助文档
        usage:help /,desc:列出所有命令的列表
        usage:test me --help ,desc:列出命令test/me 的帮助文档
    @expect 成功|失败|NONE
    """
    the_url = kwargs.get('url', '/')
    debug("打印帮助信息-url:{}".format(the_url))
    if the_url == '/':
        return router.ok_msg(show_url_list(router.routes_table.keys()))
    else:
        the_route = router.match_rule(the_url)
        if the_route is None:
            url_list = router.guess_command(the_url)
            show_url_list(url_list)
        else:
            print_one_command_help(the_url, the_route)

    return router.ok_msg('')
