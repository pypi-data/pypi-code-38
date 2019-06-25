from gencode.importmdj.import_uml_models import Import_uml_models
from gencode.uml_class_models import Class,Project
from gencode.ext import Session
import os
from jinja2 import FileSystemLoader, Environment
import codecs
import json

from sqlalchemy.orm import aliased
from sqlalchemy import or_
class ExportClass2SWGClass():
    def __init__(self,source_umlfile,dest_umlfile):
        '''

        :param source_umlfile: 源umlmodel文件
        :param dest_umlfile: 汇入swg的umlmodel文件
        '''
        self.source_umlfile = source_umlfile
        self.dest_umlfile = dest_umlfile
        self.session = Session()
        tmp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template')
        load = FileSystemLoader(tmp_path)
        self.env = Environment(loader=load)

    def _load_models(self,file):
        with codecs.open(file, encoding='utf8') as f:
            js = f.read()
            return json.loads(js)

    def __get_swg_package(self,dmodel):
        for tag in dmodel.get('tags',[]):
            if tag['name']=='swagger':
                swg_ref_id = tag['reference']['$ref']
                for elem in dmodel.get('ownedElements', []):
                    if elem['_id'] == swg_ref_id:
                        return elem
        for elem in dmodel.get('ownedElements',[]):
            if elem['name']=='swagger':
                return elem
        return []

    def export(self,exclude_classes=None):
        '''
        :param exclude_classes:不用汇出成swagger class的类名
        :return:
        '''
        if exclude_classes is None :
            exclude_classes = []
        exclude_classes = [ecls.lower() for ecls in exclude_classes]
        project = Import_uml_models(self.source_umlfile).import_model()
        classes = self.session.query(Class). \
            filter(Class.isswagger == False). \
            filter(Class.type == 'UMLClass'). \
            filter(Class.projectid == project.id).all()
        dest_model = self._load_models(self.dest_umlfile)
        swg_package = self.__get_swg_package(dest_model)
        classes_swg  = [elm['name'] for elm in swg_package.get('ownedElements',[]) if elm['_type']=='UMLClass']
        packages_swg = [elm['name'] for elm in swg_package.get('ownedElements',[]) if elm['_type']=='UMLPackage']
        classes2swg = []
        temp = self.env.get_template('swg_package_mng.tmp')
        # temp_cls = self.env.get_template('swg_class.tmp')
        for cls in classes :
            # 已产生swagger class
            if cls.name in classes_swg or \
              '%smng'%cls.name in packages_swg or \
              cls.name.lower() in exclude_classes:
                continue
            cls.assign_propertys(self.session)
            classes2swg.append(cls)
            codes = temp.render(cls_id = cls.id,
                                swg_pkg_id=swg_package['_id'],
                                cls_name = cls.name,
                                cls = cls
                                )

            swg_package.setdefault('ownedElements',[]).append(json.loads(codes,strict=False))
            # print(codes)
        # if classes2swg:
        #     temp = self.env.get_template('swg_class.tmp')
        #     codes = temp_cls.render(classes = [cls],
        #                         swg_pkg_id=swg_package['_id']
        #                         )
        #     swg_package.setdefault('ownedElements', []).extend(json.loads(codes,strict=False))
            # 取消assign的propertys
            self.session.rollback()
        with codecs.open(self.dest_umlfile,mode='w',encoding='utf-8') as file:
            file.write(json.dumps(dest_model,ensure_ascii=False))
        # self.session.rollback()
        self.session.query(Project).filter(Project.id==project.id).delete()
        print('export swagger classes success.')

if __name__ == '__main__':
    exp = ExportClass2SWGClass(r'D:\mwwork\projects\gencode\test_models\test4.mdj',
                         r'D:\mwwork\projects\gencode\test_models\test4.mdj')
    exp.export()