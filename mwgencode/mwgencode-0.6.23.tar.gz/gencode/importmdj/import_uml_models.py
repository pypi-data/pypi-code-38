from gencode.uml_class_models import *
import json
import codecs
from gencode.ext import engine,Session,Base
import logging
from mwutils.cache import Cached
from enum import Enum
from collections import namedtuple

logger = logging.getLogger('gencode.import_model')

uml_contain = ['UMLModel','UMLSubsystem','UMLPackage']
classs_uml = ['UMLClass','UMLSignal','UMLPrimitiveType','UMLDataType']

support_uml_type =('Project','UMLModel','UMLSubsystem','UMLPackage',
                   'UMLClassDiagram','UMLAttribute','UMLClass',
                   'UMLAssociation','UMLAssociationEnd','UMLSignal',
                   'UMLPrimitiveType','UMLDataType','UMLAssociationClassLink')

class Tag_type(Enum):
    boclass = 'boclass'
    swagger = 'swagger'

Tag = namedtuple('Tag',['type','value','ref_id'])

class Import_base():
    def _create_obj(self, cls, js):
        # 把所有UML class的 id 栏位增加flag
        js['id'] = self._get_id(js['id'])
        obj = cls(**js)
        self.session.add(obj)
        self.session.commit()
        return obj

    def __init__(self,session,project):
        if session is None:
            session = Session()
        self.session = session
        self.project = project

    def _get_id(self, _id):
        return '%s_%s'%(self.project.flag,_id)

    def import_elm(self,parent,elements):
        pass

    @property
    def importer(self):
        return Importer(self.project)

class Import_package(Import_base):
    def import_elm(self, parent, elements):
        assert elements['_type'] in uml_contain
        packege_js = {"id": elements['_id'],
                      "name": elements['name'],
                      "stereotype": elements.get('stereotype',''),
                      "doc": elements.get("documentation",''),
                      "type": elements['_type'],
                      "parentid":parent.id,
                      "projectid": self.project.id,
                      "isswagger": parent.isswagger or elements['name'].lower()=='swagger'
                      }
        return self._create_obj(Package, packege_js)

class Import_diagram(Import_base):
    def import_elm(self, parent, elements):
        assert elements['_type'] == 'UMLClassDiagram'
        obj_js = {"id": elements['_id'],
                      "name": elements['name'],
                      "isdefault": elements.get('defaultDiagram'),
                      "type": elements['_type'],
                      "parentid": parent.id,
                      "isswagger": parent.isswagger
                      }
        return self._create_obj(Diagram, obj_js)

class Import_property(Import_base):
    def import_elm(self, parent, elements):
        assert elements['_type'] == 'UMLAttribute'
        try:
            obj_js = {"id": elements['_id'],
                      "name": elements['name'],
                      "stereotype": elements.get('stereotype', ''),
                      "doc": elements.get("documentation", ''),
                      "type": elements.get('type','string') if not isinstance(elements.get('type','string'), dict) else 'object',
                      "multiplicity": elements.get('multiplicity', ''),
                      "isreadonly": elements.get('isReadOnly', False),
                      "isordered": elements.get('isOrdered', False),
                      "isunique": elements.get('isUnique', False),
                      "defaultvalue": elements.get('defaultValue', ''),
                      "isid": elements.get('isID', False),
                      "parentid": parent.id,
                      "isswagger": parent.isswagger,
                      "objectid": self._get_id(elements['type']['$ref']) if isinstance(elements.get('type','string'), dict) else '',
                      }
        except Exception as e:
            raise Exception('%s.elements have a error:%s,elements:%s'%(parent.name,e,elements))

        return self._create_obj(Property, obj_js)

class Import_association(Import_base):
    def __init__(self, session,project):
        super().__init__(session,project)
        # self.import_assoc_end = Import_assoc_end(session,project)

    def import_elm(self, parent, elements):
        assert elements['_type'] == 'UMLAssociation'
        obj_js = {"id":elements['_id'],
                  "name":elements.get('name',''),
                  "stereotype":elements.get('stereotype',''),
                  "doc":elements.get('documentation',''),
                  "parentid":parent.id,
                  "end1id":self._get_id(elements.get('end1',{}).get('_id')),
                  "end2id":self._get_id(elements.get('end2',{}).get('_id')),
                  "projectid":self.project.id,
                  "isswagger": parent.isswagger
                  }
        assoc = self._create_obj(Association, obj_js)
        end1 = self.importer.import_elm(assoc,elements['end1'])
        end2 = self.importer.import_elm(assoc,elements['end2'])
        return assoc

class Import_assoc_end(Import_base):
    def import_elm(self, parent, elements):
        assert elements['_type'] == 'UMLAssociationEnd'
        obj_js = {"id":elements['_id'],
                  "name":elements.get('name',''),
                  "stereotype":elements.get('stereotype',''),
                  "navigable":elements.get('navigable',False),
                  "aggregation":elements.get('aggregation',''),
                  "multiplicity":elements.get('multiplicity',''),
                  "referenceid":self._get_id(elements['reference']["$ref"]),
                  "isswagger": parent.isswagger,
                  "isderived":elements.get('isDerived',False)
                  }
        return self._create_obj(Assoc_end, obj_js)

class Import_operation(Import_base):
    def __init__(self, session,project):
        super().__init__(session,project)

    def _import_paramer(self,cls,elements):
        for elem in elements:
            self.importer.import_elm(cls, elem)

    def import_elm(self, parent, elements):
        def get_paramer_id(elms,type='in'):
            for elm in elms:
                if elm['direction']==type:
                    return self._get_id(elm['_id'])
            return ''

        def get_py_paramers(elms):
            result = []
            for elm in elms or []:
                if elm['direction']=='in':
                    def_value = elm.get('defaultValue','')
                    result.append(elm['name']+ ' = %s'%def_value if def_value else elm['name'])
            return ','.join(result)

        assert elements['_type'] == 'UMLOperation'
        obj_js = {"id":elements['_id'],
                  "name":elements.get('name',''),
                  "stereotype":elements.get('stereotype',''),
                  "doc":elements.get('documentation',''),
                  "parentid":parent.id,
                  "in_param_id":get_paramer_id(elements.get('parameters',[]),'in'),
                  "return_param_id":get_paramer_id(elements.get('parameters',[]),'return'),
                  "isswagger": parent.isswagger,
                  "py_params":get_py_paramers(elements.get('parameters')),
                  "isstatic":elements.get('isStatic',False),
                  "isquery":elements.get('isQuery',False),
                  "isabstract":elements.get('isAbstract',False),
                  "specification":elements.get('specification','')
                  }
        operation = self._create_obj(Operation, obj_js)
        self._import_paramer(operation,elements.get('parameters',[]))
        return operation

class Import_paramer(Import_base):
    def import_elm(self, parent, elements):
        assert elements['_type'] == 'UMLParameter'
        obj_js = {"id":elements['_id'],
                  "name":elements.get('name',''),
                  "stereotype":elements.get('stereotype',''),
                  "multiplicity":elements.get('multiplicity',''),
                  "type":elements['type'] if not isinstance(elements['type'],dict) else 'object',
                  "object_type_id":self._get_id(elements['type']['$ref']) if isinstance(elements['type'],dict) else '',
                  "isswagger": parent.isswagger,
                  }
        return self._create_obj(Parameter, obj_js)

class Import_enumeration(Import_base):
    def import_eitem(self,parent,literals):
        for li in literals:
            self.importer.import_elm(parent,li)

    def import_elm(self, parent, elements):
        assert elements['_type'] == 'UMLEnumeration'
        obj_js = {"id":elements['_id'],
                  "name":elements.get('name',''),
                  "stereotype":elements.get('stereotype',''),
                  "doc":elements.get('documentation',''),
                  "packageid":parent.id,
                  "isswagger": parent.isswagger,
                  "projectid":self.project.id
                  }

        enumera =  self._create_obj(Enumeration, obj_js)
        self.import_eitem(enumera,elements['literals'])

class Import_enumeitem(Import_base):
    def import_elm(self, parent, elements):
        assert elements['_type'] == 'UMLEnumerationLiteral'
        obj_js = {"id":elements['_id'],
                  "name":elements.get('name',''),
                  "stereotype":elements.get('stereotype',''),
                  "doc":elements.get('documentation',''),
                  "enumerationid":parent.id,
                  "isswagger": parent.isswagger,
                  }
        return self._create_obj(Enumeitem, obj_js)

class Import_umlgeneralization(Import_base):
    def import_elm(self, parent, elements):
        assert elements['_type'] == 'UMLGeneralization'
        obj_js = {"id":elements['_id'],
                  "stereotype":elements.get('stereotype',''),
                  # "doc":elements.get('documentation',''),
                  "parentid":self._get_id(elements['source']['$ref']),
                  "sourceid":self._get_id(elements['source']['$ref']),
                  "targetid":self._get_id(elements['target']['$ref']),
                  "isswagger": parent.isswagger,
                  "discriminator":elements.get('discriminator','')
                  }
        return self._create_obj(Umlgeneralization, obj_js)

class Import_class(Import_base):
    def __init__(self, session,project):
        super().__init__(session,project)


    def _import_attrs(self,cls,attributes):
        for attr in attributes:
            self.importer.import_elm(cls,attr)

    def _import_assocs(self,cls,assoc):
        self.importer.import_elm(cls, assoc)

    def _import_operation(self,cls,ops):
        for op in ops:
            self.importer.import_elm(cls,op)

    def _import_assoc_link(self,elem):
        ass = self.session.query(Association).filter(Association.id == self._get_id(elem['associationSide']['$ref'])).first()
        ass.is_assoc_class = True
        cls = self.session.query(Class).filter(Class.id==self._get_id(elem['classSide']['$ref'])).first()
        cls.is_assoc_class = True
        cls.assoc_id= ass.id
        ass.assoc_class_id=cls.id
        self.session.add(ass)
        self.session.add(cls)
        self.session.commit()

    def _import_elements(self,cls,elements):
        for elem in elements:
            if elem['_type'] == 'UMLAssociation':
                self._import_assocs(cls, elem)
            elif elem['_type'] == 'UMLAssociationClassLink':
                self._import_assoc_link(elem)
            elif elem['_type'] in ('UMLClass','UMLGeneralization'): #汇入关联类
                self.importer.import_elm(cls,elem)
            else:
                logger.warning('the uml type(%s) is not support in class(%s)' % (
                    elem['_type'], elem.get('name')))

    def import_elm(self, parent, elements):
        assert elements['_type'] in classs_uml,'not support the class(%s)'%elements['_type']
        obj_js = {"id": elements['_id'],
                  "name": elements['name'],
                  "stereotype": elements.get('stereotype',''),
                  "type": elements['_type'],
                  "parentid": parent.id,
                  "doc":elements.get("documentation",''),
                  "isabstract":elements.get('isAbstract',False),
                  "isswagger": parent.isswagger,
                  "projectid":self.project.id
                  }
        cls = self._create_obj(Class, obj_js)
        self._import_attrs(cls,elements.get('attributes',[]))
        self._import_elements(cls,elements.get('ownedElements',[]))
        self._import_operation(cls,elements.get('operations',[]))
        return cls

class Importer(metaclass=Cached):
    def _reg_importor(self,types,importor):
        if isinstance(types,list):
            for tp in types:
                self._importor[tp] = importor
        else:
            self._importor[types] =importor

    def _init_importor(self):
        # self._reg_importor("Project", Import_project(self.session,self.project))
        self._reg_importor(uml_contain, Import_package(self.session,self.project))
        self._reg_importor('UMLClassDiagram', Import_diagram(self.session,self.project))
        self._reg_importor(classs_uml, Import_class(self.session,self.project))
        self._reg_importor("UMLAttribute",Import_property(self.session,self.project))
        self._reg_importor("UMLAssociation",Import_association(self.session,self.project))
        self._reg_importor("UMLAssociationEnd",Import_assoc_end(self.session,self.project))
        self._reg_importor("UMLOperation",Import_operation(self.session,self.project))
        self._reg_importor("UMLParameter",Import_paramer(self.session,self.project))
        self._reg_importor("UMLEnumeration",Import_enumeration(self.session,self.project))
        self._reg_importor("UMLEnumerationLiteral",Import_enumeitem(self.session,self.project))
        self._reg_importor("UMLGeneralization", Import_umlgeneralization(self.session, self.project))

    def __init__(self,project):
        self.session = Session()
        self.project = project
        self._importor = {}
        self._init_importor()

    def import_elm(self, parent, elements):
        importor = self._importor.get(elements['_type'])
        if importor is None:
            logger.warning('the type(%s) is not support,will be ignore' % (
                 elements['_type']))
            return None
        return importor.import_elm(parent,elements)

class Import_uml_models():
    def _load_models(self,file):
        with codecs.open(file, encoding='utf8') as f:
            js = f.read()
            return json.loads(js)

    def _init_database(self):
        try:
            Base.metadata.drop_all(engine,checkfirst=False)
        except Exception as e:
            pass
        Base.metadata.create_all(engine)  # 创建资料库结构

    def __init__(self,file):
        self.file_name = file
        self._model_js = self._load_models(file)
        self._init_database()
        self._session = Session()
        self._importer = None

    def _import_package_elements(self, package, elements):
        for elm in elements:
            if elm["_type"] in uml_contain:
                pkg_elm = self._importer.import_elm(package, elm)
                self._import_package_elements(pkg_elm, elm.get('ownedElements',[]))
                continue
            self._importer.import_elm(package, elm)

    def _import_project_elements(self,project,elements,tag=None):
        def set_tag(package):
            if not tag:
                return
            pkg_js ={}
            if tag.type==Tag_type.swagger.value:
                pkg['isswagger'] = True
                # 指定为swagger的package需要把名称改为'swagger'，后面加载swagger时要用到
                if package.id=='%s_%s'%(project.flag,tag.ref_id):
                    if package.name !='swagger':
                        pkg_js['name']='swagger'
                    try:
                        pkg_js['stereotype'] ='%s/%s/%s'%(tag.value['name'],tag.value['ver'],tag.value.get('auth','jwt'))
                    except Exception as e:
                        raise Exception('tag.value 不符合要求，正确格式： {"name":"service_name","ver":"v1.0","auth":"jwt"}')
                self._session.query(Package.id==package.id).update(pkg_js)
        for pkg in elements:
            # 只有容器类才需要汇入
            if pkg['_type'] not in uml_contain:
                logger.warning('the pkg(%s) is not support type(%s),will be ignore'%(
                    pkg['name'],pkg['_type']
                ))
                continue
            package = self._importer.import_elm(project, pkg)
            set_tag(package)
            # if tag.type==Tag_type.swagger.value:
            #     package.isswagger = True
            #     # 指定为swagger的package需要把名称改为'swagger'，后面加载swagger时要用到
            #     if package.id=='%s_%s'%(project.flag,tag.ref_id):
            #         if package.name !='swagger':
            #             package.name='swagger'
            #         try:
            #             package.stereotype ='%s/%s'%(tag.value['name'],tag.value['ver'])
            #         except Exception as e:
            #             raise Exception('tag.value 不符合要求，正确格式： {"name":"service_name","ver":"v1.0"}')
            #     self._session.add(package)
            #     self._session.commit()
            # 汇入package的元素
            self._import_package_elements(package, pkg.get('ownedElements',[]))

    def __import_project(self,project_js):
        import random
        flag = str(random.randint(1,10000))+project_js['name']
        project = Project(**{'id': '%s_%s'%(flag,project_js['_id']),
                             'name': project_js['name'],
                             'author': project_js.get('author','cxh'),
                             'version': project_js.get('version','v1.0'),
                             'doc': project_js.get('documentation',''),
                             'flag': flag,
                             'file_name':self.file_name
                             }
                          )
        self._session.add(project)
        self._session.commit()
        return project

    def __handle_tags(self,project,tags,elments):
        def get_package(id,elments):
            for el in elments:
                if el['_id']==id:
                    return el
            return None
        if not tags:
            return False
        for tag in tags:
            ref_id = tag.get('reference',{}).get('$ref','')
            if not ref_id:
                raise Exception('名为（%s）的tag没有指定 referenc，请指定！'%tag['name'])
            pkg_ref = get_package(ref_id,elments)
            if tag['name'].lower()=='boclass':
                tag = Tag(type=Tag_type.boclass.value,value={},ref_id=ref_id)
                self._import_project_elements(project, [pkg_ref],tag)
            elif tag['name'].lower()=='swagger':
                try:
                    tag = Tag(type=Tag_type.swagger.value,
                          value=json.loads(tag.get('value','{}').replace('\'','"')),
                          ref_id = ref_id)
                except Exception as e:
                    raise  Exception('tag.value格式错误：%s,\n正确格式如：{"name":"service_name","ver":"v1.0"}，\n error:%s'%(tag.get('value','{}'),e))
                self._import_project_elements(project, [pkg_ref],tag)
            else:
                logger.warning('不支持名为（%s）的tag,只支持[%s,%s]'%(tag['name'],
                           'boclass','swagger'))
        return True

    def import_model(self):
        session = self._session
        project = session.query(Project).filter(Project.file_name==self.file_name).first()
        # 不允许同一project导入两次
        if project:
            return project
        project = self.__import_project(self._model_js)
        self._importer = Importer(project)
        if not self.__handle_tags(project,self._model_js.get('tags',[]),self._model_js['ownedElements']):
            self._import_project_elements(project, self._model_js['ownedElements'])
        return project




