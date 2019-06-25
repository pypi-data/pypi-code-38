try:  # 导入模块
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from gencode.dd_models import *
from gencode.ext import Session,engine

from gencode.utils import Keytype,FieldFrom,DBDataType,DBDataType_len,convert2dbType
uml="http://schema.omg.org/spec/UML/2.0"
xmi="{http://schema.omg.org/spec/XMI/2.1}"
_id = xmi+"id"
_type = xmi+"type"
_extension = xmi+'Extension'

class ImportModels():
    def __init__(self,underline=False,isIntID=False):
        '''
        :param underline: Id 为int 时，如果underline 为True 则关联id前加下划线
        :param isIntID: True为没有指定类型时为int id
        '''
        self.database = None
        self.tables = {}
        self.roles = []
        self.underline = underline
        self.isIntID = isIntID

    def _create_db(self,dbname,dbdesc):
        database = Databasedictionary()
        database.name = dbname
        database.description = dbdesc
        database.id = 'dbid'
        self.session = Session()
        return database
        # self.session.add(db)

    def _create_tb(self, cls):
        # print('  ')
        # print('   class:', cls.attrib)
        if cls.attrib.get('isAbstract', 'false') != 'false':
            return
        table = Tabledictionary()
        table.databasedictionaryid = self.database.id
        table.tablename = cls.attrib.get('name', None).lower().replace(' ','')
        table.id = cls.attrib.get(_id, None)
        # print('class name',tb.attrib.get('name',None))
        extens = cls.find(_extension)
        if extens is not None:
            # print('     extens:',extens.attrib)
            cls_doc = extens.find('documentation')
            if cls_doc is not None:
                # print('         doc:',cls_doc.attrib)
                table.description = cls_doc.attrib.get('value','')
            stereotype = extens.find('stereotype')
            if stereotype is not None:
                stereotype=stereotype.attrib.get('value','').split('/')
                for stype in stereotype:
                    if stype.lower().startswith('map'):
                        # 如：customerid = map{c_id}
                        table.maptablename = stype[4:-1].lower()
                        break
        return table

    def _create_idfld(self,clsidvalue):
        field = Fielddictionary()
        field.id = clsidvalue
        field.tabledictionaryid = clsidvalue
        field.fieldname = 'id'
        if self.isIntID:
            field.fieldtype = DBDataType.int.value
            field.fieldsize = DBDataType_len.int.value
        else:
            field.fieldtype = DBDataType.varchar.value
            field.fieldsize = DBDataType_len.varchar.value
        field.englishname = field.fieldname
        field.othername = field.fieldname
        field.keytype = Keytype.key.value
        field.fieldfrom = FieldFrom.database.value
        field.gb32name = field.fieldname
        field.isallownull = False
        return field


    def create_fnkeyfld(self,role):
        if role.assocmulitplicity != 1 or not role.assocnavigable:
            return None
        # role = Roledictionary()
        field = Fielddictionary()
        field.id = role.id
        field.tabledictionaryid = role.ownertableid
        tb = self.session.query(Tabledictionary).filter_by(id=role.reftableid).first()
        key_fld = tb.get_keyfield()
        # # 如果是autoint 则采用_id，传统的用id
        # get_id = lambda key_fld:'_id' if key_fld.fieldtype == 'int' and self.underline else 'id'
        # if role.assocrolename:
        #     field.fieldname = (role.assocrolename +get_id(key_fld)).lower()
        # else:
        field.fieldname = role.get_role_id(self.session)
        field.fieldtype = key_fld.fieldtype
        field.fieldsize = key_fld.fieldsize
        field.englishname = field.fieldname
        field.othername = field.fieldname
        field.keytype = Keytype.foreignkey.value
        field.fieldfrom = FieldFrom.database.value
        field.gb32name = field.fieldname
        if role.req:
           field.isallownull = False
        return field

    def _create_fld(self,attr,table):
        field = Fielddictionary()
        field.id = attr.attrib.get(_id)
        field.tabledictionaryid = table.id
        field.fieldname = attr.attrib.get('name').replace(' ','').lower()
        field.fieldtype = convert2dbType(attr.attrib.get('type').split('_')[0])
        type_s = attr.attrib.get('type').split('_')[0].lower().strip()
        if type_s.startswith('string') and len(type_s)>6:
            type_len = int(type_s[6:])
        else:
           type_len = DBDataType_len[field.fieldtype].value
        field.fieldsize = type_len
        field.englishname = field.fieldname
        field.othername = field.fieldname
        field.gb32name = field.fieldname
        field.big5name = field.fieldname
        if attr.attrib.get('isID') != 'false':
            field.keytype = Keytype.key.value
        else:
            field.keytype = Keytype.notkey.value
        if attr.attrib.get('isUnique') != 'false':
            field.repfields = field.fieldname
        field.fieldfrom = FieldFrom.database.value
        lowv = attr.find('lowerValue')
        if lowv is not None:
            # print('         lv:', lowv.attrib)
            field.fieldsize = int(lowv.attrib.get('value'))
        upperv = attr.find('upperValue')
        if upperv is not None:
            # print('         uv:', upperv.attrib)
            field.fieldsize = int(lowv.attrib.get('value'))
        defaultv = attr.find('defaultValue')
        if defaultv is not None:
            # print('         dv:', defaultv.attrib)
            field.defaultvalue = defaultv.attrib.get('value')

        # print('      attr:', attr.attrib)
        extens_attr = attr.find(_extension)
        if extens_attr is not None:
            attr_doc = extens_attr.find('documentation')
            if attr_doc is not None:
                # print('         doc:', attr_doc.attrib)
                field.gb32name = attr_doc.attrib.get('value')
            attr_stype = extens_attr.find('stereotype')
            if attr_stype is not None:
                # print('         stype:', attr_stype.attrib)
                stypes = attr_stype.attrib.get('value').split('/')
                for stype in stypes:
                    if stype.lower() == 'req':
                        field.isallownull = False
                    elif stype.lower() == 'rep':
                        field.repfields = field.fieldname.lower()
                    elif stype.lower().startswith('map'):
                        # 如：customerid = map{c_id}
                        field.mapname = stype[4:-1].lower()
                    elif stype.lower().startswith('rep'):
                        # 如：rep{id;name}
                        # stype[4:-1].split(';')=>['id','name']
                        stype_l = stype[4:-1].lower().split(';')
                        stype_l.append(field.fieldname)
                        field.repfields = ';'.join(stype_l)
                    elif stype.lower().startswith('plk'):
                        field.plkfieldcode = field.gb32name
                        field.plkfieldpath = stype[4:-1].lower()
                        field.fieldfrom = FieldFrom.lookup.value

        return field
        # self.session.add(field)

    def _create_role(self,memb,table):
        def getMultiplicitye(end):
            upperv = end.find('upperValue')
            if upperv is not None:
                # print('         uv:', upperv0.attrib)
                if upperv.attrib.get('value') == '*':
                    return 65535
                elif upperv.attrib.get('value') == '1':
                    return 1
            else:
                return 65535

        def getReqire(end):
            lowerv = end.find('lowerValue')
            if lowerv is not None:
                # print('         uv:', upperv0.attrib)
                return lowerv.attrib.get('value') != '0'
            return False

        def getRole(end0,end1,table,stereotype):
            '''
            因xmi档案不能带入navigable，只能根据end的顺序和multiplicity 来确定
            1，1 ->  1 只有单向关系
            2，* ->  1 lookup的关系 （非组合或聚合的关系视为单向）
            3，* <-> 1 组合或聚合关系 （为双向）
            '''
            if end0.attrib.get('isDerived')=='true' or end1.attrib.get('isDerived')=='true':
                return None
            role = Roledictionary()
            role.id = end0.attrib.get(_id)
            role.underline = self.underline or '_id' in stereotype
            role.ownertableid = end0.attrib.get('type', '')
            role.end1_multiplicity = getMultiplicitye(end0)
            # 取另一端的requre
            role.req = getReqire(end1)
            role.end1_rolename = end0.attrib.get('name', '').lower().replace(' ', '')
            if role == '':
                role.end1_rolename = table.tablename
            # master 和 detail 均有masterdetail role
            role.masterdetail = end0.attrib.get('aggregation') == 'composite' or\
                                end1.attrib.get('aggregation') == 'composite'
            role.end2_reftableid = end1.attrib.get('type', '')
            role.end2_rolename = end1.attrib.get('name', '').lower().replace(' ', '')
            if role.end2_rolename== '' and role.end2_reftableid==table.id:
                role.end2_rolename=table.tablename
            role.end2_multiplicity = getMultiplicitye(end1)
            role.end1_navigable = end0.attrib.get('aggregation') != 'none' or \
                             end1.attrib.get('aggregation') != 'none'
            role.end2_navigable = end0.attrib.get('aggregation') != 'none' or \
                             end1.attrib.get('aggregation') != 'none'
            # 如果aggregation 都为none 代表是单向关系,画图时需要顺着方向画
            if not role.end1_navigable and not role.end2_navigable:
                # 1 -> 1 关系只返回
                if role.end1_multiplicity == 1 and role.end2_multiplicity == 1:
                    if role.ownertableid == table.id:
                        role.end1_navigable = False
                        role.end2_navigable = True
                    else:
                        role.end1_navigable = True
                        role.end2_navigable = False
                # * -> 1 关系,1 方为True，*方为false
                elif role.end1_multiplicity == 1:
                    role.end1_navigable = True
                    role.end2_navigable = False
                else:
                    role.end1_navigable = False
                    role.end2_navigable = True
            return role

        ends = memb.findall('ownedEnd')
        if not ends:
            return []
        extens = memb.find(_extension)
        stereotype = []
        if extens is not None:
            # print('     extens:',extens.attrib)
            stereotype_s = extens.find('stereotype')
            if stereotype_s is not None:
                stereotype=stereotype_s.attrib.get('value','').split('/')
        # 任何一个memb 都会产生两个role
        role0 = getRole(ends[0],ends[1],table,stereotype)
        role1 = getRole(ends[1],ends[0],table,stereotype)
        if role0 and role1:
            return [role0,role1]
        else:
            return []

    def handle_cls(self,pkg):
        table = self._create_tb(pkg)
        if not table:
            return
        self.tables[table.id] = table
        self.session.add(table)
        attrs = pkg.findall('ownedAttribute')
        hasid = False
        for attr in attrs:
            if attr.attrib.get(_type, None) == 'uml:Property':
                field = self._create_fld(attr,table)
                if field.keytype == Keytype.key.value:
                    hasid = True
                self.session.add(field)
        if not hasid:
            self.session.add(self._create_idfld(table.id))

        members = pkg.findall('ownedMember')
        for memb in members:
            if memb.attrib.get(_type,None) == 'uml:Association':
                roles = self._create_role(memb,table)
                self.roles.extend(roles)

    def handle_pkgElm(self,pkgElms):
        for pkg in pkgElms:
            pkg_type = pkg.attrib.get(_type, None)
            # swagger 包中的uml:class不用处理
            if pkg.attrib.get('name',None) == 'swagger':
                continue
            if pkg_type == 'uml:Class':
                self.handle_cls(pkg)
            else:
                node = pkg.findall('packagedElement')
                if node:
                    self.handle_pkgElm(node)

    def init_database(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)  # 创建资料库结构
        # if current_app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        #     drop_all()
        #     create_all()
        # else:
        #     self.session.execute('DELETE FROM [dbo].[databasedictionary]')
        #     self.session.commit()

    def handleRoles(self):
        for role in self.roles:
            field = self.create_fnkeyfld(role)
            if field is not None:
                self.session.add(field)
        self.session.add_all(self.roles)
        self.session.commit()
        for role in self.roles:
            if role.assocrolename == '':
                role.assocrolename=role.reftable.tablename
        self.session.add_all(self.roles)
        self.session.commit()

    def impxml(self,file):
        self.init_database()
        self.database = self._create_db(file.split()[-1].split('.')[0],"")
        self.session.add(self.database)
        self.session.commit()
        tree = ET.parse(file)  # 分析XML文件
        root = tree.getroot()
        # print('0', root)
        for idx0,r in enumerate(root):
            # print('%d'%idx0, r.attrib)
            if r.attrib.get('name',None) != 'RootModel':
                continue
            self.handle_pkgElm(r.findall('packagedElement'))
        self.handleRoles()

if __name__ == '__main__':
    i = ImportModels()
    i.impxml(r"Untitled.xml")
    # i.impxml(r"test.xml")