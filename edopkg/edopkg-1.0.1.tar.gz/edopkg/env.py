# encoding: utf-8
import os
import sys
import getpass
import urllib
from ConfigParser import ConfigParser
#from utils import parse_ocapi
from config import EDO_CONFIG_PATH, OC_API, SECTION, ACCOUNT, INSTANCE, \
    USERNAME, CLIENT_ID, CLIENT_SECRET

class EdoEnvironment:

    def __init__(self, path=EDO_CONFIG_PATH):
        self.path = path
        self.edo_configparse = ConfigParser()
        cf = self.edo_configparse
        if not os.path.exists(path):
            #  初始化配置文件
            section= read_init_section(SECTION)
            oc_api, account, instance, username, password = read_detail_inputs()
            cf.add_section('edopkg')
            cf.set('edopkg', 'server', section)
            self.save_config(section, oc_api, account, instance, username, password)
        cf.read(path)

    def server(self, section):
        if section in self.edo_configparse.sections():
            # 重新设置服务器配置
            self.edo_configparse.set('edopkg', 'server', section)
            self.edo_configparse.write(open(self.path, 'w'))
            print u'修改成功'
        elif section:
            print u'配置名称 %s 不存在' % section

        #  显示当前服务器配置
        self.print_server_config()

    def config(self):
        self.print_server_config()
        action = read_action_input()
        cf = self.edo_configparse
        if action == 'modify':
            section = read_section_input(action, cf.sections(),
                                         cf.get('edopkg', 'server'))
            edo_config = dict(cf.items(section))
            oc_api, account, instance, username, password = read_detail_inputs(
                oc_api=edo_config['oc_api'],
                account=edo_config['account'],
                instance=edo_config['instance'],
                username=edo_config['username']
            )
        else:
            oc_api, account, instance, username, password = read_detail_inputs()
            section = read_section_input(action, cf.sections(), SECTION)

        # 保存配置
        self.save_config(section, oc_api, account, instance, username, password)

    def print_server_config(self):
        cf = self.edo_configparse
        active_section = cf.get('edopkg', 'server')
        print u'当前的默认服务器配置为 %s' % active_section
        info_template = u'%s, 账号 %s, 站点 %s '
        for section in cf.sections():
            if section == 'edopkg':
                continue
            oc_api = cf.get(section, 'oc_api')
            account = cf.get(section, 'account')
            instance = cf.get(section, 'instance')
            if section == active_section:
                head = u'  * %s:' % section
            else:
                head = u'    %s:' % section
            print ''.join([head.ljust(20), info_template % (oc_api, account, instance)])

    def save_config(self, section, oc_api, account, instance, username, password):
        cf = self.edo_configparse
        if section not in cf.sections():
            cf.add_section(section)
        cf.set(section, 'client_id', CLIENT_ID)
        cf.set(section, 'client_secret', CLIENT_SECRET)
        cf.set(section, 'oc_api', oc_api)
        cf.set(section, 'account', account)
        cf.set(section, 'instance', instance)
        cf.set(section, 'username', username)
        cf.set(section, 'password', password)
        cf.write(open(self.path, 'w'))
        print u' 配置文件已保存到：%s ' % self.path

    def load_config(self, section=''):
        if not section:
            section = self.edo_configparse.get('edopkg', 'server')
        cf = dict(self.edo_configparse.items(section))
        return cf['oc_api'], cf['account'], cf['instance'], cf['username'], \
            cf['password'], cf['client_id'], cf['client_secret']

def read_action_input():
    print u'''您可以选择：
    1.修改已存在的配置
    2.新建一个配置
    '''
    sys.stdout.write(u'您的选择[1/2](或输入其他命令退出)：')
    num = raw_input()
    if num not in ['1', '2']:
        sys.exit(0)
    return 'modify' if num == '1' else 'add'

def read_section_input(action, sections, default=''):
    while True:
        section = get_input(u'请输入配置名', default=default)
        # 检查用户输入的配置名
        if action == 'modify' and section not in sections:
            print u'不存在此配置，请确认后重新输入'
        elif action == 'add' and section in sections:
            print u'配置已存在，请确认后重新输入'
        elif not section:
            print u'配置名不能为空，请重新输入'
        else:
            break
    return section

def read_init_section(section):
    print u'''
    -----------------------------
    需要输入配置信息以进行初始化
    -----------------------------'''
    section = get_input(u'请输入配置名', default=section)
    return section

def read_detail_inputs(oc_api=OC_API, account=ACCOUNT,instance=INSTANCE,
                       username=USERNAME):
    print u'''
 -----------------------------
 请输入具体的配置数据
 -----------------------------
 '''
    while True:
        oc_api = get_input(u'oc_api(oc服务地址)', default=oc_api)
        account = get_input(u'account(账号名称)', default=account)
        instance = get_input(u'instance(站点实例)', default=instance)
        username = get_input(u'username(用户名)', default=username)

        print u'''
 -----------------------------
 您的输入：
 -----------------------------'''
        print ' oc_api: %s' % oc_api
        print ' account: %s' % account
        print ' instance: %s' % instance
        print ' username: %s' % username
        print u'''
 -----------------------------
 您确认要输入的是以上的数据么？[y/n]（确认：y | 重新输入：n）：'''
        if raw_input().lower() in ['y', '']:
            break
        else:
            print u'请重新输入数据:'

    while True:
        password = getpass.getpass('password: ')
        confirm_pwd = getpass.getpass('confirm password: ')
        if password == confirm_pwd:
            break
        else:
            print u'两次输入的密码不一致,  请重新输入'
    return oc_api, account, instance, username, password

def get_input(msg, default =''):
    msg = u' %s[%s]: ' % (msg, default)
    sys.stdout.write(msg.encode(sys.stdout.encoding))
    input_info = raw_input()
    return input_info if input_info else default

def parse_ocapi(oc_api):
    scheme, rest = urllib.splittype(oc_api)
    host = urllib.splithost(rest)[0]
    h3, port = urllib.splitport(host)
    h2 = '.'.join(h3.split('.')[-2:])
    online = ['everydo.cn', 'easydo.cn', 'everydo.com']
    host = 'oc-api.' + h2 if h2 in online else host + '/oc_api'
    return scheme + '://' + host
