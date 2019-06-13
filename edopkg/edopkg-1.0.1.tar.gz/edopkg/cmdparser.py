# encoding: utf-8
import sys
import argparse
from config import HELP_INFO, SERVER_HELP, CONFIG_HELP, CLONE_HELP, PULL_HELP, \
    PUSH_HELP, VERSION

class EdoArgParser(argparse.ArgumentParser):
    def error(self, message):
        print >> sys.stderr, u'错误的命令，以下是帮助信息'
        self.print_help()
        sys.exit(2)

def init_parse():
    parser = EdoArgParser(argument_default=argparse.SUPPRESS,
                          description=HELP_INFO,
                          epilog='edopkg %s' % (VERSION),
                          version=VERSION)
    p = parser.add_subparsers(title=u'命令')

    edo_server = p.add_parser('server', help=SERVER_HELP)
    edo_server.add_argument('section', nargs='?', action='store',help=u'配置名称')

    edo_config = p.add_parser('config', help=CONFIG_HELP)

    edo_clone = p.add_parser('clone', help=CLONE_HELP)
    edo_clone.add_argument('pkg_name', action='store', help=u'软件包名')
    edo_clone.add_argument('-s', '--section', nargs='?', action='store', help=u'配置名称')

    edo_pull = p.add_parser('pull', help=PULL_HELP)
    edo_pull.add_argument('path_filter', nargs='?', action='store', default='', help=u'要同步的文件夹/文件')
    edo_pull.add_argument('-s', '--section', nargs='?', action='store', help=u'配置名称')

    edo_push = p.add_parser('push', help=PUSH_HELP)
    edo_push.add_argument('path_filter', nargs='?', action='store',default='', help=u'要同步的文件夹/文件')
    edo_push.add_argument('-s', '--section', nargs='?', action='store', help=u'配置名称')
    return parser

def parse_args(argv=sys.argv[1:]):
    parser = init_parse()
    if not argv:
        parser.print_help()
        return '', ''
    return sys.argv[1], parser.parse_args(argv)

if '__name__' == '__main__':
    print parse_args()
