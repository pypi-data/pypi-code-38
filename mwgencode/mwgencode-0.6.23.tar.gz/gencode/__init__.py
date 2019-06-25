# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
from enum import Enum
from mwutils.utils import none2default
# from . import importxmi

# engine = create_engine('sqlite:///:memory:')
# Session = sessionmaker(bind=engine)

uml="http://schema.omg.org/spec/UML/2.0"
xmi="{http://schema.omg.org/spec/XMI/2.1}"
_id = xmi+"id"
_type = xmi+"type"
_extension = xmi+'Extension'

# 可以用来定义企业相关的规则的物件类别
bo_types=['uml:DataType','uml:Signal','uml:PrimitiveType','uml:Class']

class AttribType(Enum):
    none = 'none'
    data = 'data'
    object = 'object'

class ImportBase():
    def find_bo_classes(self, pkg_p, types=bo_types, result = None):
        # 查找package下所有符合类型的object
        if result is None:
            result = []
        pkgs = pkg_p.findall('packagedElement')
        for pkg in pkgs:
            if pkg.attrib.get(_type) in ['uml:Model', 'uml:Package', 'uml:Subsystem']:
                self.find_bo_classes(pkg, types, result)
            if pkg.attrib.get(_type, None) in types:
                result.append({'id': pkg.attrib.get(_id), 'obj': pkg})
        return result

    def _get_exten_value(self, attr,name):
        extens = attr.find(_extension)
        if extens is not None:
            stereotype = extens.find(name)
            if stereotype is not None:
                return stereotype.attrib.get('value')
        return None

    def get_stereotype(self, attr):
        return none2default(self._get_exten_value(attr,'stereotype'),'').split('/')

    def get_doc(self, attr):
        result = self._get_exten_value(attr, 'documentation')
        result = result if result else ''
        # 替换“，避免yaml出错
        return result.replace('"','\'')

    def get_operations(self, pkg):
        assert pkg.attrib.get(_type, None) in bo_types,'pkg必输是企业物件类型(%s)'%bo_types
        own_op =pkg.findall('ownedOperation')
        result = []
        for op in own_op:
            if op.attrib.get(_type)!= 'uml:Operation' :
                continue
            op_d= {}
            is_array = False
            # get,put,post,delete 等方法
            op_d['stereotype'] = self.get_stereotype(op)
            op_d['name'] = op.attrib.get('name')
            op_d['doc'] = self.get_doc(op)
            own_params = op.findall('ownedParameter')
            for param in own_params:
                type = param.attrib.get('type')
                if type is None :
                    continue
                try:
                    if type.endswith('_id'):
                        type = AttribType.data.value
                        typename = type.split('_')[0]
                    # 判断是否是数组
                    else:
                        typename = type
                        type = AttribType.object.value
                        is_array = param.find('upperValue') is not None

                except Exception as e:
                    print('参数没有指定type，example:【in:g_xxx_i(r)】，error:', e, param.attrib)
                    raise
                direction = param.attrib.get('direction')
                param_d = {#'id':param.attrib.get(_id),
                           'name':param.attrib.get('name'),
                           'type':type,
                           'typename':typename,
                           'is_array':is_array,
                           'doc':self.get_doc(param),
                           'stereotype':self.get_stereotype(param)}
                op_d[direction] = param_d
            result.append(op_d)
        return result

    def get_defaultvalue(self,attr):
        def_value = attr.find('defaultValue')
        if def_value is not None:
            return def_value.get('value')
        return ''

    def get_attributes(self, pkg):
        attrs = pkg.findall('ownedAttribute')
        result = []
        for attr in attrs:
            if attr.attrib.get(_type) != 'uml:Property':
                continue
            type = attr.attrib.get('type')
            is_array = False
            if type is None :
                typename = 'none'
                type = AttribType.none.value
            elif type.endswith('_id'):
                typename = type.split('_')[0]
                type = AttribType.data.value
                is_array = attr.find('upperValue') is not None
            # 判断是否是数组
            else:
                typename = type
                type = AttribType.object.value
                is_array = attr.find('upperValue') is not None
            result.append({#'id': attr.attrib.get(_id),
                           'name': attr.attrib.get('name'),
                           'type': type,
                           'typename': typename,
                           'is_array':is_array,
                           'doc': self.get_doc(attr),
                           'stereotype': self.get_stereotype(attr),
                           'defaultvalue':self.get_defaultvalue(attr)})
        return result

    def get_bo_class(self, pkg):
        return {'name': pkg.attrib.get('name'),
                'id' : pkg.attrib.get(_id),
                'doc': self.get_doc(pkg),
                'stereotype': self.get_stereotype(pkg),
                'type':pkg.attrib.get(_type),
                'attrs': self.get_attributes(pkg),
                'ops': self.get_operations(pkg)}
