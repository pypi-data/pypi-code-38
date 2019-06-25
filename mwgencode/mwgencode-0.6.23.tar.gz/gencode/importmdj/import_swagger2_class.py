try:  # 导入模块
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from gencode import (ImportBase,uml,xmi,_id,_type,_extension
             )
from gencode.swg2_class_models import *
from gencode.importmdj.import_uml_models import *
from gencode.ext import Session

required = lambda st: ('noreq' not in st) and ('nr' not in st)

class ImportSwagger(ImportBase):
    def __init__(self):
        self.swagger = None
        self.session = Session()
        self.project = None

    def __handle_swagger(self):
        # 记录swagger package 信息
        pkg_swg = self.session.query(Package).\
            filter(Package.name=='swagger').\
            filter(Package.projectid==self.project.id).first()
        if not pkg_swg:
            raise Exception('the project have no swagger package。')
        self.swagger = self.session.query(Swagger2).filter(Swagger2.id==pkg_swg.id).first()
        # 不需要重复创建 swagger
        if self.swagger:
            return self.swagger
        self.swagger = Swagger2()
        try:
            self.swagger.name,self.swagger.version ,*ext_sp= pkg_swg.stereotype.split('/')
            self.swagger.auth =ext_sp[0] if ext_sp else 'jwt'
        except Exception as e:
            raise Exception('the swagger stereotype define error,sample:"service_name/v1.0",error:%s'%e)
        self.swagger.resp_xml = 'xml' in ext_sp
        self.swagger.doc = pkg_swg.doc.replace('---','\n').replace('"','\'')
        self.swagger.id = pkg_swg.id
        self.session.add(self.swagger)
        self.session.commit()
        self.__handle_tags(pkg_swg.packages)


        # pkgs = pkg_swg.findall('packagedElement')

    def __get_sw_type_format(self, type):
        type = type.lower()
        if type.startswith('string') and len(type)>len('string'):
            type = 'string'
        if type == 'integer':
            return 'integer', 'int32'
        elif type == 'long':
            return 'integer', 'int64'
        elif type == 'float':
            return 'number', 'float'
        elif type == 'double':
            return 'number', 'double'
        elif type == 'string':
            return 'string', ''
        elif type == 'byte':
            return 'string', 'byte'
        elif type == 'binary':
            return 'string', 'binary'
        elif type == 'boolean':
            return 'boolean', ''
        elif type == 'date':
            return 'string', 'date'
        elif type in ('datetime', 'tdatetime'):
            return 'string', 'date-time'
        elif type == 'password':
            return 'string', 'password'
        elif type == 'file':
            return 'file', ''
        elif type == '':
            return 'string',''
        else:
            return type, ''

    def __get_in(self,st):
        'q:query,f:formdata,b:body,h:header,p:path,nr:not Request'
        if ('query' in st) or ('q' in st):
            return 'query'
        elif ('formdata' in st) or ('fd' in st) or ('f' in st):
            return 'formData'
        elif ('body' in st) or ('b' in st) or ('bd' in st):
            return 'body'
        elif ('header' in st) or ('h' in st) or ('hd' in st):
            return 'header'
        elif ('path' in st) or ('p' in st) or ('pth' in st):
            return 'path'
        # elif 'file' in st:
        #     return 'file'
        return ''

    def __get_respcode(self, action, code):
        if code in ('default','result','return'):
            if action in ['post', 'put']:
                return '201'
            elif action == 'delete':
                return '204'
            else:
                return '200'
        else:
            return code

    def __handle_tags(self,pkgs):
        for pkg in pkgs:
            tag = Tag2()
            tag.id = pkg.id
            tag.doc = pkg.doc.replace('---','\n').replace('"','\'')
            tag.name =pkg.name.lower()
            tag.swaggerid = self.swagger.id
            tag.swagger = self.swagger
            self.session.add(tag)
            self.session.commit()
            for cls in pkg.classs:
                if cls.type != Class_uml.umlsignal.value:
                    continue
                self.__handle_action(tag, cls.operations)

    def __get_path(self,tag,op_name):
        path = self.session.query(Path2).filter(Path2.name==op_name).\
            filter(Path2.tagid==tag.id).first()
        if not path:
            path = Path2()
            path.name = op_name.lower()
            path.tagid = tag.id
            path.tag = tag
            self.session.add(path)
            self.session.commit()
        return path

    def copy_lk_path(self, act):
        path_n = Path2(**act.path.to_json())
        path_n.id = None
        path_n.is_lk = True
        path_n.name = path_n.name + '_lk'
        path_n.tagid = act.path.tagid
        self.session.add(path_n)
        self.session.commit()

        act_n = Action2(**act.to_json())
        act_n.id = act_n.id+'_lk'
        act_n.is_lk = True

        act_n.pathid = path_n.id
        self.session.add(act_n)
        for param in act.params:
            param_js = param.to_json()
            param_js.pop('id')
            param_n = Param2(**param_js)
            # param_n.id = param_n.id+'_lk'
            param_n.actionid = act_n.id
            self.session.add(param_n)
        for resp in act.resps:
            resp_js = resp.to_json()
            resp_js.pop('id')
            resp_n =Resp2(**resp_js)
            # resp_n.id = resp_n.id+'_lk'
            resp_n.actionid = act_n.id
            self.session.add(resp_n)
        self.session.commit()

    def __handle_action(self, tag, ops):
        for op in ops:
            st = op.stereotype.split('/')
            path = self.__get_path(tag,op.name.lower())
            action = Action2()
            action.id = op.id
            action.summary, *action.doc = op.doc.split('---',1)
            action.ver_str = path.tag.swagger.version.replace('.', '_')
            action.doc = ''.join(action.doc).strip().replace('"','\'')
            action.has_formdata = False
            # 记录action有包含lk，需要做进一步处理
            action.include_lk = 'lk' in st
            if action.include_lk:
                st.remove('lk')
            action.is_auth = 's' in st
            if action.is_auth:
                st.remove('s')
            action.action = st[0]
            action.path =path
            action.pathid = path.id
            action.in_param_name = op.in_param.name
            action.return_param_name = op.return_param.name
            self.session.add_all([action,path])
            self.session.commit()
            self.__handle_param(action,op.in_param)
            self.__handle_resp(action,op.return_param)
            if action.include_lk:
                self.copy_lk_path(action)

    def __handle_param(self,act,in_param):
        assert in_param.object_type, 'in type 必须是object,请确认[%s.%s]名称是否有误' % (act.call_path(),in_param.name)
        assert in_param.object_type.type == Class_uml.umlprimitivetype.value, 'in type [%s.%s]必须是PrimitiveType' %(act.call_path(),in_param.object_type.name)
        for proper in in_param.object_type.propertys:
            if not proper.type :
                raise Exception('[%s %s.%s]参数必须指定类型' % (act.call_path(),in_param.object_type.name, proper.name))
            st = proper.stereotype.split('/')

            param = Param2()
            # param.id = proper.id
            param.name = proper.name.lower()
            param.in_ = self.__get_in(st)
            if not param.in_:
                raise Exception('{tag}.<<{act}>>{path}.inparam.<<{pst}>>{pname}的stereotype缺少或不支持,'
                                '合法的st如下：\n '
                                'q -> query \n'
                                'f ->formData \n '
                                'b ->body \n '
                                'h -> header \n '
                                'p -> path \n'
                                'nr -> required = False'.format(
                    tag=act.path.tag.name,act=act.action,
                    path=act.path.name,pname=proper.name,pst=proper.stereotype
                ))
            param.is_body = param.in_=='body'
            param.is_formdata = param.in_=='formData'
            param.is_header = param.in_=='header'
            param.is_path = param.in_=='path'
            param.is_query = param.in_=='query'
            if param.in_=='formData':
                act.has_formdata = True
            if proper.name=='page':
                act.has_page = True
                # self.session.add(act)
                # self.session.commit()
            param.desc = proper.doc.replace('---','\n').replace('"','\'')
            param.type,param.format = self.__get_sw_type_format(proper.type)
            param.type_attr = 'object' if proper.objectid else 'data'
            param.is_array = len(proper.multiplicity)>0
            param.required = required(st)
            param.actionid = act
            param.actionid = act.id
            if param.type_attr == 'object':
                if proper.object.type not in (Class_uml.umldatatype.value, Class_uml.umlclass.value):
                    raise Exception('%s.%s.%s 回应物件类型只能是%s和%s，不能是：%s' % (
                    act.call_path(),in_param.object_type.name,proper.name,Class_uml.umldatatype.value, Class_uml.umlclass.value, proper.object.type))
                param.ref_name = proper.object.name.lower()
                self.__set_defines(act.path.tag.swagger, proper.object)
            else:
                if  param.in_ == 'body':
                    raise Exception('%s,普通数据类型不能是body,object:%s,attr:%s' % (
                        act.call_path(),in_param.object_type.name, proper.name))
            self.session.add_all([param,act])
            self.session.commit()

    def __handle_resp(self,act,return_param):
        assert return_param.object_type, '[%s]return type 必须是object,请确认return名称是否有误'%(act.call_path())
        assert return_param.object_type.type == Class_uml.umlprimitivetype.value, '%s.return type(%s)必须是PrimitiveType' % (act.call_path(), return_param.object_type.name)
        try:
            for proper in return_param.object_type.propertys :
                # print('%s,%s,%s,%s'%(act.path.name,return_param.name,return_param.object_type.name,proper.name))
                # proper = Property()
                if not proper.type:
                    if proper.name in ('return', 'result', 'default'):
                        proper.type = 'string'
                    else:
                        raise Exception('[%s %s.%s]参数必须指定类型' % (act.call_path(),return_param.object_type.name, proper.name))
                resp = Resp2()
                # resp.id = proper.id
                resp.actionid = act.id
                # resp.action = act
                resp.type, resp.format = self.__get_sw_type_format(proper.type)
                resp.type_attr = 'object' if proper.objectid else 'data'
                resp.is_array = len(proper.multiplicity) > 0
                if resp.type_attr == 'object':
                    resp.ref_name = proper.object.name.lower()
                    resp.umlcls_type = proper.object.type
                    if resp.umlcls_type not in (Class_uml.umldatatype.value,Class_uml.umlclass.value):
                        raise Exception('%s.%s 回应物件类型只能是%s和%s，不能是：%s'%(act.call_path(),return_param.object_type.name, Class_uml.umldatatype.value,Class_uml.umlclass.value,resp.umlcls_type))
                    self.__set_defines(act.path.tag.swagger, proper.object,act.is_lk)
                resp.desc = proper.doc.replace('---','\n').replace('"','\'')

                resp.code = self.__get_respcode(act.action, proper.name)

                self.session.add(resp)
                self.session.commit()
                if proper.name in ('return','result','default'):
                    act.default_respid =resp.id
                self.session.add(act)
                self.session.commit()

        except Exception as e:
            raise Exception('%s.%s.%s.%s.%s raise error:%s'%(act.path.tag.name,act.path.name,
                return_param.name,return_param.object_type.name,proper.name,e))

    def __set_defines(self,swg,cls,is_lk=False):
        defi = self.session.query(Define2).filter(Define2.id == cls.id).first()
        if not defi:
            defi =Define2()
            defi.id = cls.id
            defi.name = cls.name.lower()
            defi.swaggerid=swg.id
            defi.is_lk = is_lk
            defi.swagger = swg
            self.session.add(defi)
            self.session.commit()
            for proper in cls.propertys:
                attr = Attr2()
                # attr.id = proper.id
                # attr.name = proper.name.lower()
                attr.name = proper.name
                attr.type, attr.format = self.__get_sw_type_format(proper.type)
                attr.type_attr = 'object' if proper.objectid else 'data'
                attr.defineid = defi.id
                attr.is_array = len(proper.multiplicity)>0
                attr.desc = proper.doc.replace('---','').replace('"','\'')
                attr.define = defi
                if attr.type_attr == 'object':
                    attr.ref_name = proper.object.name.lower()
                    self.__set_defines(swg, proper.object,is_lk)
                self.session.add(attr)
                self.session.commit()

        return defi

    def impUMLModels(self,file):
        self.importer = Import_uml_models(file)
        self.project = self.importer.import_model()
        self.__handle_swagger()
        return self.swagger

if __name__ == '__main__':
    if __name__ == '__main__':
        session = Session()
        i = ImportSwagger()
        i.impUMLModels(r"D:\mwwork\projects\gencode\docs\test3.mdj")
        print('swagger:',session.query(Swagger2).all())
        print('Path2:',session.query(Path2).all())
        print('Action2:',session.query(Action2).all())
        print('Param2:',session.query(Param2).all())
        print('Resp2:',session.query(Resp2).all())
        print('Define:', session.query(Define2).all())
        print('Attr:',session.query(Attr2).all())
        # attr = session.query(Attr2).first()
        # attr1 = attr.copy()
        # print(attr1)

