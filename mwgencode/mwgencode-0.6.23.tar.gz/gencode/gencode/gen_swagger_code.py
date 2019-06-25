from gencode.utils import  saveUTF8File, get_merge_file
from gencode.importmdj.import_swagger2_class import  ImportSwagger
from gencode.swg2_class_models import Swagger2,Path2,Action2,Tag2,Param2,Resp2
import os
from jinja2 import FileSystemLoader, Environment
from enum import Enum
from gencode.ext import Session

match = lambda fld, evalue: True if fld.fieldtype == evalue.value else False

required = lambda st: ('noreq' not in st) and ('nr' not in st)

class ProjectType(Enum):
    flask = 'flask'
    aiohttp = 'aiohttp'

right_type = {'post':'insert','put':'edit','delete':'delete','get':'view'}

def get_params(params):
    result = []
    for param in params:
        p_name = param.name
        if not param.required:
            p_name = p_name + ' = None'
        # heard 的不要写入到参数中
        if param.is_header:
            continue
        result.append(p_name)
    return ','.join(result)

class GenSwaggerCodeFromUml():
    def __init__(self, root_path, xmifile, type='flask'):
        self.type = type
        self.swagger_imp = ImportSwagger()
        self.swager = self.swagger_imp.impUMLModels(xmifile)
        self.root_path = root_path
        tmp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template')
        load = FileSystemLoader(tmp_path)
        self.env = Environment(loader=load)
        self.session = Session()

    def gen_swagger_code(self,outfile):
        codes = []
        swg = self.swager
        if self.type == ProjectType.aiohttp.value:
            swg.host = ''
        else:
            swg.host = 'host: localhost:8000'
        paths = self.session.query(Path2).\
            join(Tag2,Tag2.id==Path2.tagid).\
            join(Swagger2,Swagger2.id==Tag2.swaggerid).\
            filter(Swagger2.id==self.swager.id).\
            order_by(Swagger2.name,Tag2.name,Path2.name).all()
        template = self.env.get_template('swagger_file.yaml')
        result = template.render(swg=swg,paths=paths)  # self.defines)
        result = '\n'.join([line for line in result.split('\n') if line.strip() != ''])
        # print(result)
        codes.append(result)
        version_dir = swg.version.replace('.', '_')
        if outfile:
            filename = outfile
        else:
            fname = '%s.yaml' % swg.name
            filename = os.path.join(self.root_path, 'swagger', version_dir, fname)
        if os.path.exists(filename):
            print('the file is exists,将被覆盖！,filename:%s ' % filename)
        saveUTF8File(filename, codes)

    def gen_swagger_ctr_code(self):
        template = self.env.get_template('swg_ctrl_code.pys')
        version_dir = self.swager.version.replace('.', '_')
        for tag in self.swager.tags:
            codes = template.render(paths = tag.paths,
                                    right_type=right_type,
                                    get_params=get_params)
            codes = [line for line in codes.split('\n') if line.strip() != '']
            fname = '%s.py' % tag.name
            filename = os.path.join(self.root_path, 'app', 'api', version_dir, fname)
            if os.path.exists(filename):
                print('文件存在,将被合并,文件:%s' % filename)
                saveUTF8File(filename, get_merge_file(codes, filename))
            else:
                saveUTF8File(filename, codes)


if __name__ == '__main__':
    g = GenSwaggerCodeFromUml(r"d:\temp\swg", r"D:\mwwork\projects\its\mobile_gateway_server\docs\uml analyse.xml")
    g.gen_swagger_code()




