from gencode.gen_code import GenCode,GenProject_Sample,GenProject_Flask,GenProject_Aiohttp
import os
import argparse
import sys
from gencode.gencode.export_class2swgclass import ExportClass2SWGClass

class Gen_Code():
    def __init__(self, umlfile, rootpath, type='flask', args=None):
        # project 类型，flask，aiohttp
        self.type = type
        self.umlfile = os.path.abspath(umlfile)
        self.rootpath = os.path.abspath(rootpath)
        self.args = args

    def gen_code(self):
        '''
        产生一个完整的专案
        :return:
        '''
        if self.type=='flask':
            gp = GenProject_Flask(r'%s' % self.umlfile,
                                      r'%s' % self.rootpath)
        elif self.type=='aiohttp':
            gp = GenProject_Aiohttp(r'%s' % self.umlfile,
                                  r'%s' % self.rootpath)
        else:
            raise Exception('不支持该project type(%s)'%self.type)
        gp.gen_code()

    def gen_sample_code(self):
        '''
        产生一个包含 sample.mdj文件和gen_code_run.py单元的专案
        :return:
        '''
        gp = GenProject_Sample(r'%s' % self.umlfile,
                        r'%s' % self.rootpath)
        gp.gen_code()

    def gen_model(self,outfile='model_base.py'):
        '''
        产生model单元
        :return:
        '''
        print(self.args)
        g = GenCode(self.umlfile, self.rootpath)
        g.model(outfile=outfile)

    def gen_swagger(self):
        '''
        产生swagger.yaml单元
        :return:
        '''
        g = GenCode(self.umlfile, self.rootpath)
        g.swagger()

    def gen_export(self):
        exp = ExportClass2SWGClass(self.umlfile,self.umlfile)
        exp.export()

def main():
    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50, width=120))

    parser.add_argument('-f', '--filename',
                        # type=argparse.FileType(),
                        type = str,
                        help='指定mdj文件 (default: sample.mdj)',
                        default='default.mdj')

    parser.add_argument('-p', '--project-name',
                        help='专案名称(default: 当前目录名)',
                        default='.')

    parser.add_argument('-t', '--project-type',
                        help='专案类型 ：flask，aiohttp，default为 flask',
                        default='flask')

    subparsers = parser.add_subparsers(title='Command')

    gp_parser = subparsers.add_parser('gp', help='根据mdj的swagger模型 创建web project(gen_project)', add_help=False)
    gp_parser.set_defaults(command='gen_code')

    gp_parser = subparsers.add_parser('gsp', help='创建空白的 web project(gen_project)', add_help=False)
    gp_parser.set_defaults(command='gen_sample_code')

    gp_parser = subparsers.add_parser('gm', help='根据xmi创建umlclass 的 models_base单元 '
                                                 '-o 输出文件名称')
    gp_parser.set_defaults(command='gen_model')
    gp_parser.add_argument('-o', help='输出文件的名称', action='store_true')
    gp_parser.add_argument('-mt', help='输出文件的类型，flask为model_base.py+models.py ，sql为models.py',
                           action='store_true')

    gp_parser = subparsers.add_parser('gsw', help='根据xmi创建umlclass 的 swagger单元', add_help=False)
    gp_parser.set_defaults(command='gen_swagger')

    gp_parser = subparsers.add_parser('exp', help='把mdj的umlclass 转成 swagger class', add_help=False)
    gp_parser.set_defaults(command='gen_export')


    # gp_parser = subparsers.add_parser('gctrl', help='根据xmi创建umlclass 的 swagger ctrole单元', add_help=False)
    # gp_parser.set_defaults(command='gen_ctrl')

    if len(sys.argv)==1:
        parser.print_help()
        print('sample 1 : python gen_code.py -f ./docs/test.mdj -p d:/temp/swg -t aiohttp gp')
        print('sample 2 : gencode -f ./docs/test.mdj  -t aiohttp gp')
        print('sample 3 : gencode -f ./docs/test.mdj gp')
        print('sample 4 : gencode gp #-f gencode.mdj -t flask')
        sys.exit()
    args = parser.parse_args(sys.argv[1:])
    # print(args.u)
    gen_code = Gen_Code(r'%s'%args.filename,r'%s'%args.project_name,args.project_type,args)
    getattr(gen_code, args.command)()
    print('gen code success!')

if __name__ == '__main__':
#     # xmifile = r'./docs/test5.json'
#     # xmifile = r'D:\mwwork\projects\tianma\employee-mng\docs\employee-bo.mdj'
#     # g = GenCode(xmifile, rootpath)
#     # g.base(outfile='swagger_model.py',type='sql')
#     # # g.base(outfile='models1.py',type='flask')
#     # rootpath = r"./tests"
#     # # xmifile = r"D:\mwwork\projects\tianma\employee-mng\docs\employee-bo.mdj"
#     # xmifile = r'D:\mwwork\projects\gencode\docs\employee-test.mdj'
    rootpath = r"./tests1"
    # umlfile = r"./docs/test3.mdj"
    umlfile = r'./docs/test5.json'
    # umlfile = r"D:\mwwork\projects\its\analyse_busdata_web\busdata.mdj"
    # umlfile = r"./docs/leave_system.mdj"
    # umlfile = r'D:\mwwork\projects\its\tpeg_exchange_server_web\docs\tpeg_exchange_server.mdj'
    # umlfile = r'D:\mwwork\projects\smart_construction_site\kaoqingmng-py\docs\kaoqing.mdj'
    # p = GenProject_Flask(umlfile,rootpath)
    # p.gen_code()
    g = GenCode(umlfile,rootpath)
    g.model(outfile='models.py',type='sql')
    # p = GenProject_Flask(umlfile, rootpath)
    # p.gen_code()