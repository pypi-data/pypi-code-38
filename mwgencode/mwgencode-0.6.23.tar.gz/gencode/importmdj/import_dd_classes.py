try:  # 导入模块
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from gencode.dd_models import *
from gencode.ext import Session,engine
from gencode.importmdj.import_uml_models import Import_uml_models
from gencode.uml_class_models import *

from gencode.utils import Keytype,FieldFrom,DBDataType,DBDataType_len,convert2dbType

class ImportDDModels():
    def __init__(self):
        self.project = None
        self.database = None
        self.tables = {}
        self.roles = []

    def _create_db(self,project):
        database = Databasedictionary()
        database.name = project.name
        database.description = project.doc
        database.id = project.id
        self.session = Session()
        return database
        # self.session.add(db)

    def _create_tb(self, cls):
        if cls.isabstract:
            return
        table = Tabledictionary()
        table.databasedictionaryid = self.database.id
        table.tablename = cls.name.lower()
        table.is_assoc_table = cls.is_assoc_class
        table.isabstract = cls.isabstract
        table.id = cls.id
        table.description = cls.doc
        if cls.stereotype:
            stereotype = cls.stereotype.split('/')
            for stype in stereotype:
                if stype.lower().startswith('map'):
                    # 如：customerid = map{c_id}
                    table.maptablename = stype[4:-1].lower()
                    break
        if not table.maptablename:
            table.maptablename = table.tablename
        return table

    def _create_idfld(self,clsidvalue):
        field = Fielddictionary()
        field.id = clsidvalue
        field.tabledictionaryid = clsidvalue
        field.fieldname = 'id'
        # if self.isIntID:
        #     field.fieldtype = DBDataType.int.value
        #     field.fieldsize = DBDataType_len.int.value
        # else:
        field.fieldtype = DBDataType.varchar.value
        field.fieldsize = DBDataType_len.varchar.value
        field.englishname = field.fieldname.lower()
        field.othername = field.fieldname.lower()
        field.keytype = Keytype.key.value
        field.fieldfrom = FieldFrom.database.value
        field.gb32name = field.fieldname.lower()
        field.isallownull = False
        return field

    def _create_fld(self,attr,table):
        field = Fielddictionary()
        field.id = attr.id
        field.tabledictionaryid = table.id
        field.fieldname = attr.name.lower()
        field.fieldtype = convert2dbType(attr.type)
        type_s = attr.type.lower().strip()
        if type_s.startswith('string') and len(type_s)>6:
            type_len = int(type_s[6:])
        else:
           type_len = DBDataType_len[field.fieldtype].value
        field.fieldsize = type_len
        field.englishname = field.fieldname.lower()
        field.othername = field.fieldname.lower()
        field.gb32name = field.fieldname.lower()
        field.big5name = field.fieldname.lower()
        if attr.isid:
            field.keytype = Keytype.key.value
        else:
            field.keytype = Keytype.notkey.value
        if attr.isunique:
            field.repfields = field.fieldname.lower()
        field.fieldfrom = FieldFrom.database.value
        if attr.multiplicity:
            field.fieldsize = int(attr.multiplicity)
        field.defaultvalue = attr.defaultvalue
        field.gb32name = attr.doc
        field.doc = attr.doc
        if attr.stereotype:
            # print('         stype:', attr_stype.attrib)
            stypes = attr.stereotype.split('/')
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
                # if not field.mapname :
                #     field.mapname = field.fieldname
        return field

    def _create_role(self,memb,table):
        def getMultiplicitye(multi):
            upperv = multi.split('..')[-1]
            if upperv == '*':
                return 65535
            elif upperv == '1':
                return 1
            else:
                return 65535

        def getReqire(multi):
            lowerv = multi.split('..')[0]
            return lowerv != '0'

        def get_map_name(end):
            stereotype = end.stereotype.split('/')
            for stype in stereotype:
                if stype.lower().startswith('map'):
                    return stype[4:-1].lower()

        def get_st_code(st_name,stereotype):
            for stype in stereotype:
                if stype.lower().startswith(st_name):
                    return stype[4:-1]
            return ''

        def getRole(assoc, end1, end2, table, stereotype):
            '''
            1，1 ->  1 只有单向关系
            2，* ->  1 lookup的关系 （非组合或聚合的关系视为单向）
            3，1 <-> * 组合或聚合关系 （为双向）
            '''
            def exchange_end(end1,end2):
                # 交换end1和end2，让o2m和m2o的role关系处理起来更自然
                end1_multi = getMultiplicitye(end1.multiplicity)
                end2_multi = getMultiplicitye(end2.multiplicity)
                relationship_value = get_relationship_type(end1_multi, end2_multi,
                                                           end1.navigable, end2.navigable)
                # 1对一，如果方向反则交换
                if relationship_value == Relationship_type.o2o.value and not end2.navigable:
                    return end2,end1
                if relationship_value == Relationship_type.o2m.value and end1_multi>1:
                    return end2,end1
                elif relationship_value ==Relationship_type.m2o.value and end1_multi==1:
                    return end2, end1
                return end1,end2
            end1,end2 = exchange_end(end1,end2)
            role = Roledictionary()
            role.id = assoc.id
            role.is_assoc_table = assoc.is_assoc_class
            role.assoc_tableid = assoc.assoc_class_id
            role.underline = '_id' in stereotype
            role.ownertableid = assoc.parentid
            role.ddid = self.database.id
            role.req = 'req' in stereotype
            if not role.req:
                end_multiplicity = '0'
                if getMultiplicitye(end1.multiplicity)==1:
                    end_multiplicity = end1.multiplicity
                elif getMultiplicitye(end2.multiplicity)==1:
                    end_multiplicity = end2.multiplicity
                role.req = getReqire(end_multiplicity)
            role.ref = 'ref' in stereotype
            role.flt = get_st_code('flt',stereotype)
            role.ord = get_st_code('ord',stereotype)
            role.end1_aggregation = end1.aggregation.lower()
            role.end2_aggregation = end2.aggregation.lower()
            role.end1_multiplicity = getMultiplicitye(end1.multiplicity)
            role.end1_rolename = end1.name.lower().replace(' ', '')
            if role.end1_rolename == '':
                role.end1_rolename = end1.reference.name.lower()
            role.end1_mapid = get_map_name(end1)
            role.end1_navigable = end1.navigable
            role.end1_reftableid = end1.referenceid
            role.end2_reftableid = end2.referenceid
            role.end2_rolename = end2.name.lower().replace(' ', '')
            if role.end2_rolename== '' :
                role.end2_rolename=end2.reference.name.lower()
            role.end2_multiplicity = getMultiplicitye(end2.multiplicity)
            role.end2_navigable = end2.navigable
            role.end2_mapid = get_map_name(end2)
            # 图形上都为True或False时再图上效果一样，都为False时设为True
            if not role.end1_navigable and not role.end2_navigable:
                role.end1_navigable = True
                role.end2_navigable = True
            return role

        if not memb.end1 or not memb.end2:
            return
        stereotype = []
        if memb.stereotype:
            stereotype = memb.stereotype.split('/')
        return getRole(memb,memb.end1,memb.end2,table,stereotype)

    def __create_operations(self,table,operation):
        op = Ddoperation()
        op.parentid = table.id
        op.id = operation.id
        op.stereotype = operation.stereotype
        op.doc = operation.doc
        op.name = operation.name
        op.isabstract = operation.isabstract
        op.isquery = operation.isquery
        op.isstatic = operation.isstatic
        op.specification = operation.specification
        op.py_params = operation.py_params
        return op

    def handle_cls(self,cls):
        table = self._create_tb(cls)
        if not table:
            return
        self.tables[table.id] = table
        self.session.add(table)
        hasid = False
        for attr in cls.propertys:
            field = self._create_fld(attr,table)
            if field.keytype == Keytype.key.value:
                hasid = True
            self.session.add(field)
        if not hasid:
            self.session.add(self._create_idfld(table.id))

        for op in cls.operations:
            self.session.add(self.__create_operations(table,op))

        for assoc in cls.associations:
            roles = self._create_role(assoc, table)
            self.roles.append(roles)
        # for gen in cls.umlgeneralizations:


    def handle_classes(self):
        classes = self.session.query(Class).\
            filter(Class.isswagger==False).\
            filter(Class.type=='UMLClass').\
            filter(Class.projectid==self.project.id).all()
        for cls in classes:
            self.handle_cls(cls)

    def handle_generalization(self):
        gens = self.session.query(Umlgeneralization).\
            join(Class,Class.id==Umlgeneralization.parentid).\
            filter(Umlgeneralization.isswagger==False). \
            filter(Class.type == 'UMLClass'). \
            filter(Class.projectid == self.project.id).all()
        for gen in gens:
            stereotype = gen.stereotype.split('/')
            target = self.session.query(Tabledictionary).filter(Tabledictionary.id == gen.targetid).first()
            # target = Tabledictionary()
            target.is_sigletable='sng' in stereotype
            target.is_parentclass=True
            source = self.session.query(Tabledictionary).filter(Tabledictionary.id==gen.sourceid).first()
            # source = Tabledictionary()
            source.is_sigletable = 'sng' in stereotype
            source.parentid = target.id
            # source.parent = target
            self.session.add_all([source,target])
            self.session.commit()


    def init_database(self):
        Base.metadata.create_all(engine)  # 创建资料库结构

    def handleRoles(self):
        for role in self.roles:
            if role.end2_rolename == '':
                role.end2_rolename=role.end2_reftable.tablename.lower()
        self.session.add_all(self.roles)
        self.session.commit()

    def handleEnum(self):
        enumrations = self.session.query(Enumeration).\
            filter(Enumeration.isswagger==False).\
            filter(Enumeration.projectid==self.project.id).\
            all()
        get_value = lambda v_st,v_ind:v_st if v_st else str(v_ind)
        for enuma in enumrations:
            dbenma = DBEnumeration(id = enuma.id,
                                   name=enuma.name.lower(),
                                   doc=enuma.doc,
                                   type=enuma.stereotype.lower(),
                                   ddid=self.database.id
                                   )
            self.session.add(dbenma)
            for indx,eitm in enumerate(enuma.enumeitems,1):
                dbeitm = DBEnumeitem(id=eitm.id,
                                     name=eitm.name.lower(),
                                     doc=eitm.doc,
                                     type=dbenma.type.lower(),
                                     value = get_value(eitm.stereotype.split('value')[-1][1:-1],indx),
                                     enumerationid=eitm.enumerationid)
                self.session.add(dbeitm)
        self.session.commit()

    def impUMLModels(self,file):
        self.project = Import_uml_models(file).import_model()
        self.init_database()
        self.database = self._create_db(self.project)
        self.session.add(self.database)
        self.session.commit()
        self.handle_classes()
        self.handleRoles()
        self.handleEnum()
        self.handle_generalization()
        return self.database


if __name__ == '__main__':
    session = Session()
    i = ImportDDModels()
    i.impUMLModels(r"D:\mwwork\projects\gencode\docs\test5.json")
    print(session.query(DBEnumeration).all())
    print(session.query(DBEnumeitem).all())
    # i.impxml(r"test.xml")