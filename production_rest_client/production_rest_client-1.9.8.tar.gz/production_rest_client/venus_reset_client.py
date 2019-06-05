# #!/usr/bin/env python
# # coding=utf-8
# """
# @athor:weifeng.guo
# @data:2019/3/26 13:56
# @filename:flask_reset_client
# """
# # pylint: disable=wrong-import-position, relative-import
# import sys
# import os
# import re
# import argparse
# import platform
# sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..", "..", "..")))
# from rest_client import RestClient
#
#
# def get_function_list(file_path):
#     func_list = list()
#     class_name = None
#     for line in open(file_path).readlines():
#         if r"class Test" in line:
#             class_name = re.findall("class ([a-zA-Z_]+)", line)[0]
#
#         if r"    def test_" in line and class_name:
#             test_name = re.findall("def ([a-zA-Z0-9_]+)", line)[0]
#             func_list.append("{}:{}.{}".format(file_path, class_name, test_name))
#
#     return func_list
#
#
# def list_test_case(file_list, keyword=None):
#     for file_path in file_list:
#         if keyword:
#             if keyword in file_path:
#                 if platform.system() == "Linux":
#                     print(file_path.replace(keyword, "\033[1;31m{}\033[0m".format(keyword)))
#                 else:
#                     print(file_path)
#
#             for func_name in get_function_list(file_path):
#                 if keyword in func_name:
#                     if platform.system() == "Linux":
#                         print(func_name.replace(keyword, "\033[1;31m{}\033[0m".format(keyword)))
#                     else:
#                         print(func_name)
#         else:
#             print(file_path)
#
#
# def run(args):
#     rest_client = RestClient(args.targetip)
#     if args.list:
#         if args.cmd == "all":
#             result_list = rest_client.test_case.list(args.cmd)
#             list_test_case(result_list)
#         else:
#             result_list = rest_client.test_case.list(args.cmd)
#             list_test_case(result_list)
#     elif args.nose:
#         print(rest_client.test_case.run(None, ip=args.targetip, command=args.cmd,
#                                         loglevel=args.loglevel, controller=args.controller,
#                                         flash=args.flashtype, extra=args.extra,
#                                         nose=args.nose)['msg'])
#     elif args.regress:
#         print(rest_client.test_case.run(None, ip=args.targetip, command=args.cmd,
#                                         loglevel=args.loglevel, controller=args.controller,
#                                         flash=args.flashtype, extra=args.extra,
#                                         regress=args.regress)['msg'])
#     else:
#         print(rest_client.test_case.run(None, ip=args.targetip, command=args.cmd,
#                                         loglevel=args.loglevel, controller=args.controller,
#                                         flash=args.flashtype, extra=args.extra,
#                                         python=args.python)['msg'])
#
#
# if __name__ == '__main__':
#     PARSER = argparse.ArgumentParser(description='Restful Client')
#     PARSER.add_argument('-t', '--targetip', required=True, help='Target IP')
#     PARSER.add_argument('-c', '--controller', default='TAHOE', help='Controller of CNEX SSD')
#     PARSER.add_argument('-f', '--flashtype', default='BICS', help='Flash type of CNEX SSD')
#     PARSER.add_argument('-L', '--loglevel', default='DEBUG',
#                         choices=('DEBUG', 'INFO', 'WARN', 'ERROR'), help='Log level')
#     GROUP = PARSER.add_mutually_exclusive_group(required=True)
#     GROUP.add_argument('-l', '--list', action='store_true', help='List test cases')
#     GROUP.add_argument('-n', '--nose', action='store_true', help='Run nosetests command')
#     GROUP.add_argument('-p', '--python', action='store_true', help='Run python command')
#     GROUP.add_argument('-r', '--regress', action='store_true', help='Regress nosetests file')
#     PARSER.add_argument('cmd', help='Command Line')
#     PARSER.add_argument('extra', nargs=argparse.REMAINDER)
#     ARGS = PARSER.parse_args()
#
#     sys.exit(run(ARGS))
