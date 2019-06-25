from gencode.utils import  saveUTF8File, get_merge_file
from gencode.importmdj.import_swagger2_class import  ImportSwagger
from gencode.swg2_class_models import Swagger2,Path2,Action2,Tag2,Param2,Resp2
import os
from jinja2 import FileSystemLoader, Environment
from enum import Enum
from gencode.ext import Session
import json
import codecs

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
        if param.is_query:
            p_name = p_name + '=None'
        # heard 的不要写入到参数中
        else:
            continue
        result.append(p_name)
    return '?'+'&'.join(result) if result else ''

def get_define(ref_name,swg):
    for defn in swg.defines:
        if defn.name==ref_name:
            return defn

def get_define_js(defn,swg):
    result ={}
    for att in defn.attrs:
        if att.type_attr=='object':
            defn1 = get_define(defn.ref_name,swg)
            assert defn1, "%s's is null" % (defn.call_path())
            defn1_js = get_define_js(defn1,swg)
            if defn1.is_array:
                result[att.name] = [defn1_js]
            else:
                result[att.name] = defn1_js
            continue
        result[att.name] = '%s'%att.type
    return result

def get_resp_js(act):
    def_resp = act.default_resp
    swg = act.path.tag.swagger
    defn = get_define(def_resp.ref_name,swg)
    if not defn:
        result =''
    else:
        result = get_define_js(defn,swg)
    if def_resp.is_array:
        return [result]
    return result

class GenTestsCodeFromUml():
    def __init__(self, root_path, xmifile, type='flask'):
        self.type = type
        self.swagger_imp = ImportSwagger()
        self.swager = self.swagger_imp.impUMLModels(xmifile)
        self.root_path = root_path
        self.tmp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template','tests')
        load = FileSystemLoader(self.tmp_path)
        self.env = Environment(loader=load)
        self.session = Session()
    def save_as(self,sfile,dfile):
        if os.path.exists(dfile):
            print('the file(%s) is exist'%dfile)
            return
        with codecs.open(sfile,encoding='utf8') as f:
            codes = f.readlines()
            saveUTF8File(dfile,[code.rstrip() for code in codes])

    def __gen_test_classmng_code(self):
        template = self.env.get_template('test_classmng.pys')
        for tag in self.swager.tags:
            fname = 'test_%s.py' % tag.name
            filename = os.path.join(self.root_path, 'tests', fname)
            if os.path.exists(filename):
                print('测试文件存在,文件:%s' % filename)
                continue
            codes = template.render(tag = tag,
                                    get_params=get_params,
                                    get_resp_js = get_resp_js
                                    )
            codes = [line for line in codes.split('\n') if line.strip() != '']
            saveUTF8File(filename, codes)

    def gen_tests_codes(self):
            self.__gen_test_classmng_code()
            self.save_as(os.path.join(self.tmp_path ,'__init__.pys'),
                         os.path.join(os.path.realpath(self.root_path),'tests', '__init__.py'))
            self.save_as(os.path.join(self.tmp_path, 'run.pys'),
                         os.path.join(os.path.realpath(self.root_path), 'tests', 'run.py'))
            self.save_as(os.path.join(self.tmp_path, 'init_test_data.pys'),
                         os.path.join(os.path.realpath(self.root_path), 'tests', 'init_test_data.py'))
            saveUTF8File(os.path.join(os.path.realpath(self.root_path),'tests', 'test_base.py'),
                         [self.env.get_template('test_base.pys').render(swagger=self.swager)],
                         exist_ok=False
                         )



