from .gencode.gen_bo_models_code import Gen_bo_models
from .gencode.gen_swagger_code import  GenSwaggerCodeFromUml
from .gencode.gen_tests_code import  GenTestsCodeFromUml
import os
import shutil
from gencode.utils import saveUTF8File
import codecs
from gencode.gencode.export_class2swgclass import ExportClass2SWGClass

class GenCode():
    def __init__(self,modelfile,rootpath):
        '''
        :param modelfile: mdj 文件
        :param rootpath: 专案根目录
        :param appdir:   model文件放入的目录
        '''
        assert modelfile.endswith('.mdj') or modelfile.endswith('.json'), \
               'modelfile 必须为 modelfile，扩展名为.mdj'
        self.modelfile = os.path.abspath(modelfile)
        self.rootpath = os.path.abspath(rootpath)

    def model(self, outfile='models_base.py', type='flask',appdir='app',exists2cover=True):
        '''
        产生基本资料的base类别的代码
        :param outfile: bomodel的文件名
        :param type:  flask:flask_sqlalchemy 的 model
                      sql :' sqlalchemy 的 model
        :return:
        '''
        if appdir:
            outfile_name = os.path.join(self.rootpath,appdir, outfile)
        else:
            outfile_name = os.path.join(self.rootpath, outfile)
        gen_code = Gen_bo_models(self.modelfile,
                                 outfile_name,
                                 type=type)
        gen_code.gen_code(exists2cover)

    def swagger(self,outfile='swagger.yaml',type='flask'):
        '''
        产生swagger.yaml文件
        :param outfile:
        :param type:
        :return:
        '''
        imp = GenSwaggerCodeFromUml(self.rootpath,self.modelfile,type)
        imp.gen_swagger_code(os.path.join(self.rootpath,outfile))

    def export(self,source_umlfile,dest_umlfile,exclude_classes=None):
        export = ExportClass2SWGClass(source_umlfile,dest_umlfile)
        export.export(exclude_classes)

class GenProject_base():
    def __init__(self,modelfile,rootpath):
        # project 类型，flask，aiohttp
        self.modelfile = os.path.abspath(modelfile)
        self.rootpath = os.path.abspath(rootpath)
        self.tmp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gencode', 'template')
        self.sample_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gencode', 'sample')
        # 创建其他专案文件
        from jinja2 import FileSystemLoader, Environment
        load = FileSystemLoader(self.tmp_path)
        self.env = Environment(loader=load)

    def save_as(self,sfile,dfile):
        if os.path.exists(dfile):
            print('the file(%s) is exist'%dfile)
            return
        with codecs.open(sfile,encoding='utf8') as f:
            codes = f.readlines()
            saveUTF8File(dfile,[code.rstrip() for code in codes])

class GenProject_Sample(GenProject_base):
    def __init__(self,modelfile,rootpath):
        super().__init__(modelfile,rootpath)
        
    def gen_code(self):
        p_name = os.path.split(self.rootpath)[-1]
        if not os.path.exists(self.modelfile):
            if not os.path.exists('docs'):
                os.makedirs('docs')

            # shutil.copy(os.path.join(self.sample_path, 'sample.mdj'),
            #             os.path.join(os.path.realpath(self.rootpath),'docs', '%s.mdj'%p_name))
            self.template = self.env.get_template('sample.mdj')
            saveUTF8File(os.path.join(os.path.realpath(self.rootpath),'docs', '%s.mdj'%p_name),
                         [self.template.render(service_name=p_name)],
                         writegeninfo=False)
        gen_code_file = os.path.join(os.path.realpath(self.rootpath), 'gen_code_run.py')
        if not os.path.exists(gen_code_file):
            self.template = self.env.get_template('gen_code_run.pys')
            saveUTF8File(gen_code_file,
                         [self.template.render(pro_name=p_name)])

class GenProject_Aiohttp(GenProject_base):
    def __init__(self,modelfile,rootpath):
        super().__init__(modelfile,rootpath)

    def gen_code(self):
        g = GenSwaggerCodeFromUml(self.rootpath, self.modelfile, type='aiohttp')
        # outfile为’‘时，采用默认的路径
        g.gen_swagger_code(outfile='')

class GenProject_Flask(GenProject_base):
    def __init__(self,modelfile,rootpath):
        super().__init__(modelfile,rootpath)

    def gen_code(self,
                 include_swagger:bool=True,
                 include_model:bool=True,
                 include_test:bool = False,
                 include_seeds:bool = False,
                 use_uwsgi:bool = True,
                 plugins:list = None):
        '''
        创建专案文件
        :param include_swagger: False 不产生swagger file 和 swagger相关代码
        :param include_model: False 不产生model，model_base等相关代码
        :param include_test: False 不产生test相关代码
        :param include_seeds: False 不产生seeds相关代码
        :param use_uwsgi: False 不产生uwsgi相关代码
        :param plugins: 支持redis,kafka,cassandra等,默认支持redis
        :return:
        '''
        if plugins is None:
            plugins= ['redis']
        elif isinstance(plugins,list):
            plugins.append('redis')
        else:
            plugins = ['redis',plugins]
        # outfile为’‘时，采用默认的路径
        gen = GenSwaggerCodeFromUml(self.rootpath, self.modelfile, type='flask')
        if include_swagger:
            gen.gen_swagger_code(outfile='')
            gen.gen_swagger_ctr_code()
        else:
            print('提示：不产生swagger file')
        saveUTF8File(os.path.join(os.path.realpath(self.rootpath),'app','__init__.py'),
                     [self.env.get_template('__init__.pys').render(swagger = gen.swager,
                                                             include_model=include_model,plugins=plugins)],
                     exist_ok=False
                     )
        saveUTF8File(os.path.join(os.path.realpath(self.rootpath), 'README.md'),
                     [self.env.get_template('README.md').render(swagger = gen.swager)],
                     exist_ok=False
                     )
        saveUTF8File(os.path.join(os.path.realpath(self.rootpath), 'Dockerfile'),
                     [self.env.get_template('Dockerfile.tmp').render(swagger=gen.swager)],
                     exist_ok=False)
        saveUTF8File(os.path.join(os.path.realpath(self.rootpath), 'docker-compose.yaml'),
                     [self.env.get_template('docker-compose.yaml').render(root_path=os.path.split(self.rootpath)[-1],
                                                                swagger=gen.swager,plugins=plugins)],
                     exist_ok=False)
        saveUTF8File(os.path.join(os.path.realpath(self.rootpath), 'docker-compose-dev.yaml'),
                     [self.env.get_template('docker-compose-dev.yaml').render(root_path=os.path.split(self.rootpath)[-1],
                                                                swagger=gen.swager,plugins=plugins)],
                     exist_ok=False)
        saveUTF8File(os.path.join(os.path.realpath(self.rootpath), 'run.py'),
                     [self.env.get_template('run.pys').render(root_path=os.path.split(self.rootpath)[-1],
                                                                swagger=gen.swager)],
                     exist_ok=False)

        saveUTF8File(os.path.join(os.path.realpath(self.rootpath), 'uwsgi_run.py'),
                         [self.env.get_template('uwsgi_run.pys').render(root_path=os.path.split(self.rootpath)[-1],
                                                                swagger=gen.swager)],
                         exist_ok=False
                         )

        self.save_as(os.path.join(self.sample_path,'config.ini'),
                     os.path.join(os.path.realpath(self.rootpath), 'config.ini'))

        saveUTF8File(os.path.join(os.path.realpath(self.rootpath), 'config.py'),
                     [self.env.get_template('config.pys').render(include_model=include_model)],
                     exist_ok=False
                     )
        self.save_as(os.path.join(self.sample_path,'config-sample.ini'),
                     os.path.join(os.path.realpath(self.rootpath),'config-sample.ini'))
        self.save_as(os.path.join(self.sample_path,'babel.cfg'),
                     os.path.join(os.path.realpath(self.rootpath), 'babel.cfg'))
        self.save_as(os.path.join(self.sample_path,'gen_code_run.pys'),
                     os.path.join(os.path.realpath(self.rootpath),'gen_code_run.py'))
        self.save_as(os.path.join(self.sample_path, 'requirements.txt'),
                     os.path.join(os.path.realpath(self.rootpath), 'requirements.txt'))
        self.save_as(os.path.join(self.sample_path, 'gitignore.git'),
                     os.path.join(os.path.realpath(self.rootpath), '.gitignore'))
        self.save_as(os.path.join(self.sample_path, 'dockerignore.dock'),
                     os.path.join(os.path.realpath(self.rootpath), '.dockerignore'))
        self.save_as(os.path.join(self.sample_path, 'run.sh'),
                     os.path.join(os.path.realpath(self.rootpath), 'run.sh'))
        self.save_as(os.path.join(self.sample_path, 'run.sh'),
                     os.path.join(os.path.realpath(self.rootpath), 'run-dev.sh'))
        self.save_as(os.path.join(self.sample_path, 'utils.pys'),
                     os.path.join(os.path.realpath(self.rootpath),'app', 'utils.py'))
        if include_model:
            self.save_as(os.path.join(self.sample_path, 'utils.pys'),
                         os.path.join(os.path.realpath(self.rootpath), 'app', 'utils.py'))
            self.save_as(os.path.join(self.sample_path, 'migrate_run.pys'),
                         os.path.join(os.path.realpath(self.rootpath), 'migrate_run.py'))
            self.save_as(os.path.join(self.sample_path, 'migrate_run.bat'),
                         os.path.join(os.path.realpath(self.rootpath), 'migrate_run.bat'))
            self.save_as(os.path.join(self.sample_path, 'migrate_run.bat'),
                         os.path.join(os.path.realpath(self.rootpath), 'migrate_run.sh'))
        if include_seeds:
            self.save_as(os.path.join(self.sample_path, 'config.ini'),
                         os.path.join(os.path.realpath(self.rootpath), 'seeds', 'config.ini'))
            self.save_as(os.path.join(self.sample_path,'seeds', 'models_rm.pys'),
                         os.path.join(os.path.realpath(self.rootpath),'seeds', 'models_rm.py'))
            self.save_as(os.path.join(self.sample_path,'seeds', 'seed_dev_data.pys'),
                         os.path.join(os.path.realpath(self.rootpath),'seeds', 'seed_dev_data.py'))
            self.save_as(os.path.join(self.sample_path,'seeds', 'seed_init.pys'),
                         os.path.join(os.path.realpath(self.rootpath),'seeds', 'seed_init.py'))
            self.save_as(os.path.join(self.sample_path,'seeds', 'seed_rm.pys'),
                         os.path.join(os.path.realpath(self.rootpath),'seeds', 'seed_rm.py'))
            # 在seeds中不能执行
            self.save_as(os.path.join(self.sample_path,'seeds','seed_run.pys'),
                         os.path.join(os.path.realpath(self.rootpath), 'seed_run.py'))
            self.save_as(os.path.join(self.sample_path,'seeds', 'seed_utils.pys'),
                         os.path.join(os.path.realpath(self.rootpath),'seeds', 'seed_utils.py'))

        if include_test:
            gen_test_code = GenTestsCodeFromUml(self.rootpath, self.modelfile, type='flask')
            gen_test_code.gen_tests_codes()
            # self.save_as(os.path.join(self.sample_path, 'test__init__.pys'),
            #              os.path.join(os.path.realpath(self.rootpath),'tests', '__init__.py'))
            # self.save_as(os.path.join(self.sample_path, 'test_run.pys'),
            #              os.path.join(os.path.realpath(self.rootpath), 'tests', 'run.py'))
            # saveUTF8File(os.path.join(os.path.realpath(self.rootpath),'tests', 'test_base.py'),
            #              [self.env.get_template('test_test_base.tmp').render(service_name=gen.swager.name)],
            #              exist_ok=False
            #              )

        if use_uwsgi:
            saveUTF8File(os.path.join(os.path.realpath(self.rootpath), 'default.conf'),
                         [self.env.get_template('default.conf').render(port=80)],
                         exist_ok=False
                         )
            saveUTF8File(os.path.join(os.path.realpath(self.rootpath), 'supervisord.conf'),
                         [self.env.get_template('supervisord.conf').render(swagger=gen.swager)],
                         exist_ok=False
                         )
            saveUTF8File(os.path.join(os.path.realpath(self.rootpath), 'uwsgi.ini'),
                         [self.env.get_template('uwsgi.ini').render(swagger=gen.swager,plugins=plugins)],
                         exist_ok=False
                         )
            saveUTF8File(os.path.join(os.path.realpath(self.rootpath), 'uwsgi-dev.ini'),
                         [self.env.get_template('uwsgi.ini').render(swagger=gen.swager,plugins=plugins)],
                         exist_ok=False
                         )

