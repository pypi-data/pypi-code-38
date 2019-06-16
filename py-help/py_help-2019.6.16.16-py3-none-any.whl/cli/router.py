# -*- coding: utf-8 -*-
import copy
import difflib
import json
import os
import re
import subprocess
import sys
import time

from ..api_help.api_info_generator import ApiInfoGenerator
from ..lib.CommonLogger import debug, info, warn, error, set_log_level, print_ex
from ..lib.cdaemon import ClientDaemon

# 获取当前终端的行宽和高度，用于格式化打印
ROW, COLUMN = map(lambda x: int(x), subprocess.check_output(
    ['stty', 'size']).split()) if sys.stdout.isatty() else [0, 20]

DAEMON_SET_FILE = '/var/log/py_help_daemon.set'


class Router:
    '''Routing'''
    routes_table = {}
    route_group_table = {'child': {}, 'father': None, 'type': 'group'}
    is_import_controller = False
    is_run_in_daemon = False
    extra_cmds = {
        'debug': False,
        'help': False,
        'daemon': False,
        'detail': False
    }

    @classmethod
    def add_route(cls, rule, handler, route_info):
        """
        加入路由表
        将每个接口设定的路由规则加入路由表，分为简单规则表与正则规则表。简单规则直接加入，正则规则先预编译成pattern实例。
        Args:
            rule: 路由规则
            handler: 路由的处理函数
            route_info : 路由信息
        """
        if route_info is None:
            error("{rule}路由信息没有正确解析".format(rule=rule))
        if not rule.startswith('/'):
            rule = "/{}".format(rule)
        the_route = cls.routes_table.get(rule, None)
        if the_route is None:
            debug("添加路由表项:{r}".format(r=rule))
            the_node_dict = {
                'rule': rule,
                'handler': handler,
                'route_info': route_info,
            }
            cls.routes_table[rule] = the_node_dict
            the_rule_arr = rule.split('/')
            father_group = cls.route_group_table
            for i in range(0, len(the_rule_arr)):
                one_rule = the_rule_arr[i]
                the_group = father_group.get('child', {}).get(one_rule, None)
                # 下面生成group 树形结构
                if the_group is None:
                    if i < len(the_rule_arr) - 1:
                        debug("[{len}],[{i}]添加route group one_rule:{o},full_rule:{full}".format(i=i,
                                                                                                len=len(the_rule_arr),
                                                                                                o=one_rule, full=rule))
                        father_group.get('child')[one_rule] = {
                            'father': father_group,
                            'type': 'group',
                            'node': None,
                            'child': {}
                        }
                        father_group = father_group.get('child')[one_rule]
                    else:
                        debug("添加route one_rule:{o},full_rule:{full}".format(o=one_rule, full=rule))
                        father_group['child'][one_rule] = {
                            'father': father_group,
                            'type': 'node',
                            'node': the_node_dict,
                            'child': {}
                        }
                        break
                else:
                    debug("获取到分组: [{}] url:{}".format(one_rule, rule))
                    if i < len(the_rule_arr) - 1:
                        if the_group.get('type') == 'node':
                            debug("这个分组本身就是一个命令:{},url{}".format(one_rule, rule))
                            the_group['type'] = 'group'
                        father_group = the_group
                    else:
                        debug("这个分组本身就是一个命令:{}".format(one_rule))
                        father_group['node'] = the_node_dict
                        break
        else:
            warn("尝试重复添加路由:{r},{hdl}".format(r=rule, hdl=handler))
        return the_route

    @classmethod
    def match_rule(cls, the_rule):
        '''路由匹配
        规则：首先搜索简单规则表，不匹配则再搜索正则规则表
        Args:
            the_rule: 路由项字符串
        Returns:
            dict: 路由表项
        '''
        # Search for static routes first
        route = cls.routes_table.get(the_rule, None)
        if route is None:
            debug('没有找到路由:{}'.format(the_rule))
            debug("the_table:{}".format(cls.routes_table))
        else:
            return route

    @classmethod
    def get_rules(cls, pattern='.*', include_private=True):
        regx = re.compile(r'^%s' % pattern)
        rules1 = [(route_dict.get('rule'), route_dict.get('handler'), route_dict.get('public'))
                  for rule, route_dict in router.routes_simple.items() if
                  regx.match(rule) and (include_private or route_dict.get('public'))]
        rules2 = [(route_dict.get('rule'), route_dict.get('handler'), route_dict.get('public'))
                  for route_dict in router.routes_regexp if
                  regx.match(route_dict.get('rule')) and (include_private or route_dict.get('public'))]
        rules = rules1 + rules2
        return rules

    @classmethod
    def run(cls, argv):
        debug('输入指令为: vst ' + ' '.join(argv))
        return cls().run_orig(argv)

    @classmethod
    def get_route_groups_dict(cls):
        return cls.route_group_table

    @classmethod
    def ok_msg(cls, out_msg):
        return {'exit': 0, "out": out_msg}

    @classmethod
    def fail_msg(cls, out_msg):
        return {'exit': 1, "out": out_msg}

    @staticmethod
    def handle_controller_ret(is_exit, ret):
        if isinstance(ret, dict) and ret.get('exit') is not None and ret.get('out') is not None:
            if isinstance(ret.get('out'), dict) or isinstance(ret.get('out'), list):
                print(json.dumps(ret.get('out'), indent=4, sort_keys=True, ensure_ascii=False))
            else:
                print(ret.get('out'))
            if is_exit:
                sys.exit(ret.get('exit'))
                return
        else:
            if isinstance(ret, dict):
                print(json.dumps(ret, indent=4, sort_keys=True, ensure_ascii=False))
            elif ret is not None:
                print(ret)
        if is_exit:
            sys.exit(0)

    def __init__(self):
        self.url = '/'
        self.params = {}
        self.extra_cmds = copy.copy(self.__class__.extra_cmds)

    def run_backend_task(self, argv):
        '''
        后台任务的入口,用于调度后台任务
        :param argv: 参数的命令行数组
        :return: 输出任务ID
        '''
        ClientDaemon.daemon_stop('backend')
        ClientDaemon.daemon_run('backend', self.run_orig, argv)

    def run_daemon(self, argv, try_time=2):
        import rpyc
        from ..lib.rpyc_server import RpycServer
        try:
            the_class = str(self.__class__)
            debug("is start run {arg} class[{the_class}]".format(arg=argv, the_class=the_class))
            conn = rpyc.connect('localhost', 56188, config={"allow_public_attrs": True})
            debug("connect ok")
            ret = json.loads(
                conn.root.run_the_cmd(json.dumps({'argv': argv, 'class_name': the_class}),
                                      the_stderr=sys.stderr))
            debug("run ok")
            conn.close()
            return self.handle_controller_ret(is_exit=True, ret=ret)
        except Exception as e:
            if try_time > 0:
                ClientDaemon.daemon_stop('py_help_daemon')
                ClientDaemon.daemon_run('py_help_daemon', RpycServer.run_service)
                time.sleep(1)
                return self.run_daemon(argv, try_time - 1)
            else:
                error("try_time {t} is over get exception again".format(t=try_time), e)

    def add_param(self, raw):
        raw = raw.lstrip('-')
        [k, v] = raw.split('=') if '=' in raw else [raw, True]
        self.params[k] = v

    def handle_all_argv(self, argv):
        pre_url_list = []
        url_found = False
        for index, one_arg in enumerate(argv):
            if self.__class__.extra_cmds.get(one_arg) is not None:
                self.extra_cmds[one_arg] = True
                continue
            if not one_arg.startswith('--'):
                if url_found:
                    warn("不支持空格分割的参数,--xxx=abc形式的参数::{}".format(one_arg))
                else:
                    debug("添加一个路由:{}".format(one_arg))
                    pre_url_list.append(one_arg.replace('/', "\\"))
                    self.url = '/' + '/'.join(pre_url_list) if len(pre_url_list) > 0 else '/'
            else:
                if not url_found:
                    self.url = '/' + '/'.join(pre_url_list) if len(pre_url_list) > 0 else '/'
                    url_found = True
                    info('命令{all}已经找到url了:{arg}'.format(all=','.join(argv), arg=one_arg))
                self.add_param(one_arg)
        debug("最后获取到的url是:{url},参数:{params}".format(url=self.url, params=self.params))

    def run_orig(self, argv, is_exit=True):
        '''路由入口'''

        if 'backend' in argv or '--_backend=y' in argv or '--_backend' in argv:
            debug("backend URL:{url},Args:{args}".format(url=self.url, args=argv))
            if 'backend' in argv:
                argv.remove('backend')
            if '--_backend=y' in argv:
                argv.remove('--_backend=y')
            if '--_backend' in argv:
                argv.remove('--_backend')
            # 预处理参数后再传进去
            self.handle_all_argv(argv)
            return self.run_backend_task(argv)
        elif (not self.__class__.is_run_in_daemon) and ('daemon' in argv or os.path.exists(DAEMON_SET_FILE)):
            debug("daemon URL:{url},Args:{args}".format(url=self.url, args=argv))
            if 'daemon' in argv:
                argv.remove('daemon')
            # 预处理参数后再传进去
            self.handle_all_argv(argv)
            return self.run_daemon(argv)
        else:
            # 预处理参数后再传进去
            self.handle_all_argv(argv)
            return self.real_call(is_exit)

    @classmethod
    def guess_command(cls, the_url):
        guest_url = []
        for one_url in cls.routes_table.keys():
            seq = difflib.SequenceMatcher(lambda x: x in " \\t/", one_url, the_url)
            ratio = seq.ratio()
            if ratio > 0.6:
                guest_url.append(one_url)
        if len(guest_url) == 0:
            for one_url in cls.routes_table.keys():
                if the_url in one_url:
                    guest_url.append(one_url)
        print("命令 {url} 没有找到\n".format(url=the_url))
        print("您是否要跑以下命令::\n".format(url=the_url))
        for one_url in guest_url:
            print("\t{url}\n".format(url=' '.join(one_url.split('/'))))
        return guest_url

    def import_controller(self):
        '''
        这个函数需要用户复写,用于加载用户的相关的工具
        :return:
        '''
        warn("这里需要自己实现自己的import逻辑")
        self.is_import_controller = True

    def real_call(self, is_exit=True):
        """
        调用方法
        执行匹配到的接口函数
        """
        if not self.__class__.is_import_controller:
            # 加载所有路由
            from . import builtin_command
            self.import_controller()
            self.is_import_controller = True
            self.__class__.is_import_controller = True

        if self.extra_cmds['help']:
            if self.url is None:
                self.url = '/'
            debug("是一个帮助命令{}".format(self.url))
            route = self.__class__.match_rule('/help')
        else:
            route = self.__class__.match_rule(self.url)
        if self.extra_cmds['debug']:
            set_log_level('debug')
        debug("route:{}".format(route))
        if route is None and self.url != '/':
            self.__class__.guess_command(self.url)
            if is_exit:
                return self.handle_controller_ret(True, {'exit': 1, 'out': 'Error: VST command not found.'})
            else:
                return {}
        else:
            if self.extra_cmds['help'] or self.url == '/':
                debug("是一个帮助命令{}".format(self.url))
                route = self.__class__.match_rule('/help')
                self.params['url'] = self.url
            debug("需要call {}".format(route))
            handler = route.get('handler')
            # 入口打印日志
            debug("URL:{},Handler:{},Args:{}".format(self.url, handler, self.params))
            old_stdout = sys.stdout
            try:
                # 调用路由目标，并将返回值打印到控制台，并指定程序的退出码
                sys.stdout = sys.stderr
                time_before = time.time()
                ret = handler(**self.params)
                time_after = time.time()
                info('finish, time spend {}s'.format(round(time_after - time_before, 2)))
                sys.stdout = old_stdout
                debug("call url:{url},ret:{ret}".format(url=self.url, ret=ret))
                self.handle_controller_ret(is_exit, ret)
                return ret
            except Exception as es:
                msg = '跑命令{url}出现错误'.format(url=self.url)
                msg += print_ex(es)
                error(msg)
                return self.handle_controller_ret(True, {'exit': 1, "out": msg})
            finally:
                sys.stdout = old_stdout


'''
Initiate a router
'''
router = Router
