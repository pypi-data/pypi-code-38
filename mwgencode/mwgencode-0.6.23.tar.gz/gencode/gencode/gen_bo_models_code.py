'''
产生 boclass 的model
'''

from gencode.dd_models import *
from gencode.utils import Keytype,FieldFrom,saveUTF8File
from gencode.ext import Session
from enum import Enum
import os
from jinja2 import FileSystemLoader, Environment
from gencode.importmdj.import_dd_classes import ImportDDModels
from collections import OrderedDict

MODELS_PY = 'models.py'

class DBTable_meta():
    def __init__(self):
        self.class_name = ''
        self.table_name = ''
        self.columns = []

class DBTable():
    def __init__(self):
        self.class_name = ''
        self.table_name = ''
        # 继承关系的父类名称
        self.parent_name = ''
        self.is_parent_class = False
        # 单表继承
        self.is_sigletable = False
        self.mapper_args = ''
        # orm sql 不产生 output “__table_args__ = {'implicit_returning': False}”
        self.table_args = {}
        self.discriminator_column = None
        self.columns = []
        self.relationsips = []
        self.unique_constraints = []
        self.fkeyids = []
        self.funcs= []
        self.doc = ''
    def __repr__(self):
        return 'name:%s,doc:%s'%(self.table_name,self.doc)

class DBFunc():
    def __init__(self,name):
        self.name =name
        self.isabstract = False
        self.isquery = False
        self.isstatic = False
        self.params = ''
        self.codes = ''
        self.doc = ''
        self.self_param =''

class DBColumn():
    def __init__(self,name):
        # self.foreign_key = ''
        self.primary_key = ''
        self.name = name
        self.dbname= ''
        self.type = ''
        self.default = ''
        self.sys_default = ''
        self.unique = ''
        self.nullable = ''
        self.doc = ''

class Enume_model():
    def __init__(self,name):
        self.name = name
        self.columns = {}

class DBColumn_fkeyid(DBColumn):
    def __init__(self,name):
        super().__init__(name)
        self.reftable = ''
        self.refid = ''

class DBRelationship():
    def __init__(self,name):
        self.name = name
        self.relationship_cls = ''
        self.uselist = ''
        self.foreign_keys = ''
        self.back_populates = ''
        self.secondary = ''
        self.cascade = ''
        self.lazy = ''
        self.remote_side = ''
        self.primaryjoin = ''
        self.order_by = ''

class Gen_type(Enum):
    flask ='flask' # flask_sqlalchemy 的 model
    sql = 'sql' # sqlalchemy 的 model

class BoCodeGenerator_base():
    def __init__(self,database_dict):
        self.database_dict = database_dict
        # self.codes = []
        self.tables_js=OrderedDict()
        # self.dbtables = {}
        self.tables_meta_js={}
        self.enmumerations_js=[]
        self.session = Session()
        # 如：db.Model,db.Column
        self.model_prefix = ''
        # 类的后缀，如_base 。。。
        self.class_suffix = ''
        self.template_file = ''
        # 把parentclass排前面，确保子类能引用
        self.tables = self.session.query(Tabledictionary).\
            filter(Tabledictionary.databasedictionaryid==self.database_dict.id).\
            order_by(Tabledictionary.is_parentclass.desc()).all()

    def __load_template(self, temp_file_name):
        tmp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template')
        load = FileSystemLoader(tmp_path)
        env = Environment(loader=load)
        return env.get_template(temp_file_name)

    def covert2pytype(self,dbtype, size):
        if dbtype == 'bit':
            return '{model_pre}Boolean'.format(model_pre=self.model_prefix)
        elif dbtype == 'char' or dbtype == 'varchar' or \
                        dbtype == 'nchar':
            return '{model_pre}String({size})'.format(model_pre=self.model_prefix,
                                                      size=size)
        elif dbtype == 'datetime':
            return '{model_pre}DateTime'.format(model_pre=self.model_prefix)
        elif dbtype == 'time':
            return '{model_pre}Time'.format(model_pre=self.model_prefix)
        elif dbtype == 'float':
            return '{model_pre}Float'.format(model_pre=self.model_prefix)
        elif dbtype == 'int':
            return '{model_pre}Integer'.format(model_pre=self.model_prefix)
        elif dbtype == 'numeric':
            return '{model_pre}Float'.format(model_pre=self.model_prefix)
        elif dbtype == 'text':
            return '{model_pre}Text'
        elif dbtype == 'AutoInt':
            return 'db.Integer'.format(model_pre=self.model_prefix)
        elif dbtype == 'date':
            return '{model_pre}Date'.format(model_pre=self.model_prefix)
        elif dbtype == 'image':
            return '{model_pre}LargeBinary'.format(model_pre=self.model_prefix)

    def __validDefault(self, fld, defvalue):
        pytype = self.covert2pytype(fld.fieldtype, fld.fieldsize)
        if pytype.startswith('{modle_pre}Boolean'.format(modle_pre=self.model_prefix)):
            return defvalue.capitalize()
        elif pytype.startswith('{modle_pre}String'.format(modle_pre=self.model_prefix)):
            return '%s' % defvalue if defvalue.startswith('\'') else '"%s"' % defvalue
        elif pytype.startswith('{modle_pre}DateTime'.format(modle_pre=self.model_prefix)) or \
                pytype.startswith('{modle_pre}Date'.format(modle_pre=self.model_prefix)):
            if defvalue.lower().find('now') != -1 or \
                            defvalue.lower().find('today') != -1 or \
                            defvalue.lower().find('date') != -1:
                if defvalue.lower().find('+') != -1:
                    # 程序
                    s = defvalue.lower().split('+')
                    return 'datetime.now()+timedelta(days=%s)' % s[-1]
                else:
                    # 插入时间
                    return 'datetime.now'
            else:
                return defvalue
        else:
            return defvalue

    def __gen_o2o_code(self,role):
        ''''''
        '''
        class Parent(Base):
            child = relationship("Child", uselist=False, back_populates="parent")
        '''
        assert role.end1_multiplicity == 1 and role.end2_multiplicity == 1
        # 如果是单向的一对一，转为多对一处理
        if not role.end1_navigable and role.end2_navigable:
            role.end1_multiplicity=65535
            return self.__gen_m2o_code(role)
        # fkeys_end1 = self.tables_js[role.end1_reftable.tablename].setdefault('f_keys', {})
        fkeys_end1 = DBRelationship(role.end2_rolename)
        fkeys_end1.relationship_cls= role.end2_reftable.tablename.capitalize()
        fkeys_end1.foreign_keys =', foreign_keys="{end2_cls}.{fkey}"'.format(end2_cls=role.end2_reftable.tablename.capitalize(),
                                    fkey=role.end1_foreign_key_name,)
        fkeys_end1.uselist = ',uselist=False'
        fkeys_end1.back_populates = ', back_populates = "{end1_role}"'.format(end1_role=role.end1_rolename) # if role.end1_navigable else ''
        self.tables_js[role.end1_reftable.tablename].relationsips.append(fkeys_end1)
        '''
        class Child(Base):
            parent_id = Column(Integer, ForeignKey('parent.id'))
            parent = relationship("Parent", back_populates="child")
        '''
        # fkeys_end2 = self.tables_js[role.end2_reftable.tablename].setdefault('f_keys', {})
        dbtable = self.tables_js[role.end2_reftable.tablename]
        end1_tb_idfld = role.end1_reftable.get_keyfield()
        column = DBColumn_fkeyid(role.end1_foreign_key_name)
        column.dbname = '' if not role.end1_mapid  else '"%s",' % role.end1_mapid.lower()
        column.type = self.covert2pytype(end1_tb_idfld.fieldtype, end1_tb_idfld.fieldsize)
        column.reftable = self.__get_table_name(role.end1_reftable) #.maptablename.lower()
        column.refid = end1_tb_idfld.fieldname if not end1_tb_idfld.mapname else end1_tb_idfld.mapname
        column.nullable = ', nullable= False' if role.req else ''
        dbtable.fkeyids.append(column)
        fkeys_end2 = DBRelationship(role.end1_rolename)
        fkeys_end2.relationship_cls = role.end1_reftable.tablename.capitalize()
        fkeys_end2.foreign_keys = ', foreign_keys="{end2_cls}.{fkey}"'.\
            format(end2_cls=role.end2_reftable.tablename.capitalize(),
                   fkey=role.end1_foreign_key_name)
        fkeys_end2.back_populates = ', back_populates="{end2_role}"'.\
            format(end2_role=role.end2_rolename)
        dbtable.relationsips.append(fkeys_end2)

    def __get_table_name(self,table):
        # 单表模式继承，且为son类，tablename用parent的
        if table.is_sigletable and table.parent:
            table = table.parent
        tablename = table.tablename.lower() \
            if table.maptablename is None \
            else table.maptablename.lower()
        return tablename

    def __gen_m2o_code(self,role):
        ''''''
        '''
        class Parent(Base):
            child_id = Column(Integer, ForeignKey('child.id'))
            child = relationship("Child")
        class Child(Base):
        '''
        assert role.end1_multiplicity > 1 and role.end2_multiplicity == 1
        dbtable = self.tables_js[role.end1_reftable.tablename]
        end2_tb_idfld = role.end2_reftable.get_keyfield()
        column = DBColumn_fkeyid(role.end2_foreign_key_name)
        column.dbname = '' if not role.end2_mapid  else '"%s",' % role.end2_mapid.lower()
        column.type = self.covert2pytype(end2_tb_idfld.fieldtype, end2_tb_idfld.fieldsize)
        column.reftable = self.__get_table_name(role.end2_reftable) #role.end2_reftable.maptablename
        column.refid = end2_tb_idfld.fieldname if not end2_tb_idfld.mapname else end2_tb_idfld.mapname
        column.nullable = ', nullable= False' if role.req else ''
        dbtable.fkeyids.append(column)
        fkeys_end1 = DBRelationship(role.end2_rolename)
        fkeys_end1.relationship_cls = role.end2_reftable.tablename.capitalize()
        fkeys_end1.foreign_keys = ', foreign_keys="{end1_cls}.{fkey}"'.\
            format( end1_cls=role.end1_reftable.tablename.capitalize(),
                    fkey=role.end2_foreign_key_name)
        if role.is_tree():
            fkeys_end1.remote_side =', remote_side=[%s]'%role.end1_reftable.get_keyfield().fieldname

        # fkeys_end1.uselist = ', uselist=False'
        dbtable.relationsips.append(fkeys_end1)

    def __gen_o2m_code(self, role):
        ''''''
        '''
        class Parent(Base):
            children = relationship("Child", back_populates="parent")
        '''
        assert role.end1_multiplicity==1 and role.end2_multiplicity>1
        dbtable_end1 = self.tables_js[role.end1_reftable.tablename]
        fkeys_end1 = DBRelationship('%ss' % role.end2_rolename)
        fkeys_end1.relationship_cls = role.end2_reftable.tablename.capitalize()
        fkeys_end1.foreign_keys =  ', foreign_keys="{end2_cls}.{fkey}"'.format(
                            end2_cls=role.end2_reftable.tablename.capitalize(),
                            fkey=role.end1_foreign_key_name)
        fkeys_end1.back_populates ='{back_populates}'.format(
                            back_populates = ', back_populates="{end1_role}"'.format(end1_role=role.end1_rolename) if role.end1_navigable else ''
                            )
        fkeys_end1.lazy = ', lazy="dynamic"' if not role.is_md() else ''
        fkeys_end1.cascade = ', cascade="all, delete-orphan"' if role.is_md() else ''
        if role.flt:
            if 'remote' in role.flt or 'foreign' in role.flt:
                fkeys_end1.primaryjoin = ' ,primaryjoin={flt}'.format(flt=role.flt)
            else:
                fkeys_end1.primaryjoin = ' ,primaryjoin="and_({end1_cls}.{end1_key}=={end2_cls}.{end2_fkey},{flt})"'.format(
                    end1_cls=role.end1_reftable.tablename.capitalize(),
                    end1_key=role.end2_reftable.get_keyfield().fieldname,
                    end2_cls=role.end2_reftable.tablename.capitalize(),
                    end2_fkey=role.end1_foreign_key_name,
                    flt=role.flt
                )

        if role.ord:
            fkeys_end1.order_by = ', order_by="{ord_fld}"'.format(ord_fld=role.ord)
        dbtable_end1.relationsips.append(fkeys_end1)
        '''
        class Child(Base):
            parent_id = Column(Integer, ForeignKey('parent.id'))
            parent = relationship("Parent", back_populates="children")
        '''
        dbtable_end2 = self.tables_js[role.end2_reftable.tablename]
        end1_tb_idfld = role.end1_reftable.get_keyfield()
        column = DBColumn_fkeyid(role.end1_foreign_key_name)
        column.dbname = '' if not role.end1_mapid  else '"%s",' % role.end1_mapid.lower()
        column.type = self.covert2pytype(end1_tb_idfld.fieldtype, end1_tb_idfld.fieldsize)
        column.reftable = self.__get_table_name(role.end1_reftable)#.maptablename.lower()
        column.refid = end1_tb_idfld.fieldname if not end1_tb_idfld.mapname else end1_tb_idfld.mapname
        column.nullable = ', nullable= False' if role.req else ''
        dbtable_end2.fkeyids.append(column)
        if role.end1_navigable:
            fkeys_end2 = DBRelationship(role.end1_rolename)
            fkeys_end2.relationship_cls = role.end1_reftable.tablename.capitalize()
            fkeys_end2.foreign_keys = ', foreign_keys="{end2_cls}.{fkey}"'.format(
                       end2_cls=role.end2_reftable.tablename.capitalize(),
                       fkey=role.end1_foreign_key_name)
            fkeys_end2.back_populates = ', back_populates="{end2_roles}"'.format(
                       end2_roles='%ss' % role.end2_rolename)
            if role.is_tree():
                fkeys_end2.remote_side = ', remote_side=[%s]'%role.end1_reftable.get_keyfield().fieldname
            dbtable_end2.relationsips.append(fkeys_end2)

    def __gen_m2m_code4assoc(self, role):
        # def get_reftable(table):
        #     # 单表模式继承，且为son类，tablename用parent的
        #     if table.is_sigletable and table.parent:
        #         return table.parent.maptablename.lower()
        #     else:
        #         return table.maptablename.lower()
        ''''''
        '''
        class Association(Base):
            left_id = Column(Integer, ForeignKey('left.id'), primary_key=True)
            right_id = Column(Integer, ForeignKey('right.id'), primary_key=True)
            child = relationship("Child", back_populates="parents")
            parent = relationship("Parent", back_populates="children")
        '''
        assert role.end1_multiplicity>1 and role.end2_multiplicity>1
        dbtable_assoc = self.tables_js[role.assoc_table.tablename]
        end1_tb_idfld = role.end1_reftable.get_keyfield()
        column1 = DBColumn_fkeyid(role.end1_foreign_key_name)
        column1.dbname = '' if not role.end1_mapid  else '"%s",' % role.end1_mapid.lower()
        column1.type = self.covert2pytype(end1_tb_idfld.fieldtype, end1_tb_idfld.fieldsize)
        column1.reftable = self.__get_table_name(role.end1_reftable) #.maptablename.lower()
        column1.refid = end1_tb_idfld.fieldname if not end1_tb_idfld.mapname else end1_tb_idfld.mapname
        column1.primary_key = ', primary_key=True'
        dbtable_assoc.fkeyids.append(column1)

        end2_tb_idfld = role.end2_reftable.get_keyfield()
        column2 = DBColumn_fkeyid(role.end2_foreign_key_name)
        column2.dbname = '' if not role.end2_mapid  else '"%s",' % role.end2_mapid.lower()
        column2.type = self.covert2pytype(end2_tb_idfld.fieldtype, end2_tb_idfld.fieldsize)
        column2.primary_key = ', primary_key=True'
        column2.reftable = self.__get_table_name(role.end2_reftable) #role.end2_reftable.maptablename.lower()
        column2.refid = end2_tb_idfld.fieldname if not end2_tb_idfld.mapname else end2_tb_idfld.mapname
        dbtable_assoc.fkeyids.append(column2)
        fkeys_end1 = DBRelationship(role.end1_rolename)
        fkeys_end1.relationship_cls = role.end1_reftable.tablename.capitalize()
        fkeys_end1.foreign_keys = ', foreign_keys="{assoc_cls}.{fkey}"'.format(
                assoc_cls = role.assoc_table.tablename.capitalize(),
                fkey= role.end1_foreign_key_name,
               )
        fkeys_end1.back_populates = ', back_populates="{end2_roles}"'.format(
                 end2_roles='%ss'%role.end2_rolename
               )
        dbtable_assoc.relationsips.append(fkeys_end1)
        fkeys_end2 = DBRelationship(role.end2_rolename)
        fkeys_end2.relationship_cls = role.end2_reftable.tablename.capitalize()
        fkeys_end2.foreign_keys = ', foreign_keys="{assoc_cls}.{fkey}"'.format(
            assoc_cls=role.assoc_table.tablename.capitalize(),
            fkey=role.end2_foreign_key_name
        )
        fkeys_end2.back_populates = ', back_populates="{end1_roles}"'.format(
            end1_roles='%ss' % role.end1_rolename
        )
        dbtable_assoc.relationsips.append(fkeys_end2)

        '''
        class Parent(Base):
            children = relationship("Association", back_populates="parent")
        '''
        dbtable_end1 = self.tables_js[role.end1_reftable.tablename]
        fkeys_end1 = DBRelationship('%ss' % role.end2_rolename)
        fkeys_end1.relationship_cls = role.assoc_table.tablename.capitalize()
        fkeys_end1.foreign_keys =', foreign_keys="{assoc_cls}.{fkey}"'.format(
                     assoc_cls=role.assoc_table.tablename.capitalize(),
                     fkey=role.end1_foreign_key_name
                )
        fkeys_end1.back_populates = ', back_populates="{end1_role}"'.format(
                     end1_role=role.end1_rolename
                )
        dbtable_end1.relationsips.append(fkeys_end1)

        '''
        class Child(Base):
            parents = relationship("Association", back_populates="child")
        '''
        dbtable_end2 = self.tables_js[role.end2_reftable.tablename]
        fkeys_end2 = DBRelationship('%ss' % role.end1_rolename)
        fkeys_end2.relationship_cls = role.assoc_table.tablename.capitalize()
        fkeys_end2.foreign_keys =', foreign_keys="{assoc_cls}.{fkey}"'.format(
                     assoc_cls=role.assoc_table.tablename.capitalize(),
                     fkey=role.end2_foreign_key_name
                )
        fkeys_end2.back_populates = ', back_populates="{end2_role}"'.format(
                     end2_role=role.end2_rolename
                )
        dbtable_end2.relationsips.append(fkeys_end2)

    def __gen_m2m_code(self, role):
        '''
        :param role:
        :return:
        '''
        '''
        association_table = Table('association', Base.metadata,
            Column('left_id', Integer, ForeignKey('left.id')),
            Column('right_id', Integer, ForeignKey('right.id'))
        )
        '''
        assert role.end1_multiplicity>1 and role.end2_multiplicity>1
        tablename = self.__get_table_name(role.assoc_table)
        # tablename = role.assoc_table.tablename.lower() \
        #             if role.assoc_table.maptablename is None \
        #              else role.assoc_table.maptablename.lower()
        table_meta_class =self.tables_meta_js[tablename] = DBTable_meta()
        table_meta_class.class_name = role.assoc_table.tablename.lower()
        table_meta_class.table_name = tablename
        end1_tb_idfld = role.end1_reftable.get_keyfield()
        column0 = DBColumn_fkeyid(role.end1_foreign_key_name)
        column0.dbname = role.end1_foreign_key_name
        column0.type = self.covert2pytype(end1_tb_idfld.fieldtype, end1_tb_idfld.fieldsize)
        column0.reftable = self.__get_table_name(role.end1_reftable)#self.role.end1_reftable.maptablename.lower()
        column0.refid = end1_tb_idfld.fieldname if not end1_tb_idfld.mapname else end1_tb_idfld.mapname
        table_meta_class.columns.append(column0)

        end2_tb_idfld = role.end2_reftable.get_keyfield()
        column1 = DBColumn_fkeyid(role.end2_foreign_key_name)
        column1.dbname = role.end2_foreign_key_name
        column1.type = self.covert2pytype(end2_tb_idfld.fieldtype, end2_tb_idfld.fieldsize)
        column1.reftable = self.__get_table_name(role.end2_reftable)#.maptablename.lower()
        column1.refid = end2_tb_idfld.fieldname if not end2_tb_idfld.mapname else end2_tb_idfld.mapname
        table_meta_class.columns.append(column1)

        '''
        class Parent(Base):
            children = relationship("Child",
            secondary=association_table,
            back_populates="parents")
        '''
        dbtable_end1 = self.tables_js[role.end1_reftable.tablename]
        fkeys_end1 = DBRelationship('%ss' % role.end2_rolename)
        fkeys_end1.relationship_cls = role.end2_reftable.tablename.capitalize()
        fkeys_end1.secondary =',secondary={tablename} '.format(tablename=tablename)
        fkeys_end1.back_populates = ', back_populates="{end1_roles}"'.format(
                                      end1_roles='%ss' % role.end1_rolename
                        )
        dbtable_end1.relationsips.append(fkeys_end1)

        '''
        class Child(Base):
            parents = relationship("Parent",
            secondary=association_table,
            back_populates="children")
        '''
        dbtable_end2 = self.tables_js[role.end2_reftable.tablename]
        fkeys_end2 = DBRelationship('%ss' % role.end1_rolename)
        fkeys_end2.relationship_cls = role.end1_reftable.tablename.capitalize()
        fkeys_end2.secondary =',secondary={tablename} '.format(tablename=tablename)
        fkeys_end2.back_populates = ', back_populates="{end2_roles}"'.format(
                                      end2_roles='%ss' % role.end2_rolename
                        )
        dbtable_end2.relationsips.append(fkeys_end2)

    def __gen_model_code(self):
        for table in self.tables:
            # 不包含属性的多对多关系直接产生meta table
            if table.is_assoc_table and len(table.fielddictionarys)==1:
                continue

            tablename = table.tablename.lower() if table.maptablename is None \
                else table.maptablename.lower()
            table_js= DBTable()
            table_js.doc = (table.description or '').replace('\n','\n    ')
            self.tables_js[table.tablename]=table_js
            bo_class = table.tablename.capitalize()
            table_js.class_name = bo_class
            table_js.table_name = tablename
            table_js.is_sigletable = table.is_sigletable
            # 是单表继承
            if table.is_sigletable:
                # 父类，需要增加识别栏位
                if table.is_parentclass:
                    # discriminator = db.Column('type', db.String(50))
                    column = DBColumn('discriminator')
                    column.type = '{model_pre}String({size})'.format(model_pre=self.model_prefix,
                                                                     size=50)
                    column.dbname = '"type",'
                    table_js.discriminator_column = column
                    table_js.mapper_args = "{'polymorphic_on': discriminator}"
                    table_js.is_parent_class = True
                elif table.parent :
                    # 子类不需要 table
                    table_js.mapper_args = "{'polymorphic_identity': '%s'}"%tablename
                    table_js.table_name = ''
                    table_js.parent_name = table.parent.tablename.capitalize()
                else:
                    assert False,'not suport'

            for fld in table.fielddictionarys:
                fld_name = fld.fieldname.replace(' ', '')
                column = DBColumn(fld_name)
                column.doc = (fld.doc or '').replace('\n','. ')
                column.type = self.covert2pytype(fld.fieldtype, fld.fieldsize)
                column.dbname = '' if fld.mapname is None else '"%s",' % fld.mapname.lower()
                if fld.keytype == Keytype.key.value :
                    # 关联表使用使用外键做key
                    if table.is_assoc_table:
                        continue
                    # 单表继承关系的子类不需要id
                    if table.is_sigletable and table.parent:
                        continue
                    column.primary_key = ', primary_key=True'
                    if fld.fieldtype in ('int','AutoInt'):
                        table_js.table_args['implicit_returning'] = False
                elif fld.fieldfrom == FieldFrom.database.value:
                    pass
                else:
                    continue
                column.nullable =', nullable= False' if not fld.isallownull else ''
                column.unique =', unique= True' if fld.repfields == fld.fieldname else ''
                column.default= ', default= %s' % self.__validDefault(fld, fld.defaultvalue) if fld.defaultvalue else ''
                table_js.columns.append(column)
                # 多栏位不能重复
                if fld.repfields and fld.repfields != fld.fieldname:
                    repflds = fld.repfields.split(';')
                    # 把fieldname替换成资料库的mapname
                    repflds = [fld.mapname if fld.mapname is not None and repfld == fld.fieldname else repfld for repfld
                               in repflds]
                    consraint = "{model_pre}UniqueConstraint({rep_flds}, name='unique_{table_name}_{comp_name}')" .format (
                                     model_pre = self.model_prefix,
                                     rep_flds = ','.join(["'%s'" % rf for rf in repflds]),
                                     table_name = table.tablename,
                                     comp_name = '_'.join([rf for rf in repflds]))
                    table_js.unique_constraints.append(consraint)
            for op in table.ddoperations:
                func = DBFunc(op.name)
                func.isstatic = op.isstatic
                func.isquery = op.isquery
                func.isabstract = op.isabstract
                func.params = ',%s'%op.py_params if op.py_params else ''
                func.self_param = 'cls' if op.isstatic else 'self'
                func.codes = '    pass' if op.isabstract else op.specification
                func.doc = op.doc
                table_js.funcs.append(func)
        roles = self.session.query(Roledictionary).\
            filter(Roledictionary.ddid==self.database_dict.id).all()
        for role in roles:
            if role.is_o2o():
                self.__gen_o2o_code(role)
            elif role.is_m2o():
                self.__gen_m2o_code(role)
            elif role.is_o2m():
                self.__gen_o2m_code(role)
            elif role.is_m2m():
                if role.assoc_table is None:
                    raise Exception('the role 缺少关系定义，如：1-->*,%s'%role)
                # 如果关联类包含栏位，需要做为类出现，否则只需要meta 类即可
                if len(role.assoc_table.fielddictionarys)>1:
                    self.__gen_m2m_code4assoc(role)
                else:
                    self.__gen_m2m_code(role)
        dbenumerations = self.session.query(DBEnumeration).\
            filter(DBEnumeration.ddid == self.database_dict.id).all()
        for dbenum in dbenumerations:
            enum_model = Enume_model(dbenum.name.capitalize())
            self.enmumerations_js.append(enum_model)
            for eitm in dbenum.enumeitems:
                enum_model.columns[eitm.name] = '"%s"'%eitm.value if eitm.type=='string' else eitm.value

        return self.tables_js

    def gen_code(self,outfile,exists2cover=True):
        tables = self.__gen_model_code()
        template = self.__load_template(self.template_file)
        # print(self.tables_meta_js)
        result = template.render(tables= tables,
                                 metatables= self.tables_meta_js,
                                 enumerations= self.enmumerations_js)
        codes = [line for line in result.split('\n') if line.strip() != '']
        import os
        if exists2cover and os.path.exists(outfile):
            print('the file is exists,将被覆盖！,filename:%s' % outfile)
        elif not exists2cover and os.path.exists(outfile):
            print('the file is exists,不允许覆盖！,filename:%s' % outfile)
            return
        saveUTF8File(outfile, codes)

class BoCodeGenerator_flask(BoCodeGenerator_base):
    '''
    创建flask的model
    '''
    def __init__(self,database_dict):
        super().__init__(database_dict)
        # 如：db.Model,db.Column
        self.model_prefix = 'db.'
        # 类的后缀，如_base 。。。
        self.class_suffix = '_base'
        self.template_file = 'flask_models_base.pys'

    def _get_models_class_code(self,outfile):
        import os
        import codecs
        codes = []
        models_file = os.path.join(os.path.dirname(outfile), MODELS_PY)
        if os.path.exists(models_file):
            with codecs.open(models_file, "r", "utf-8") as file:
                for code in file.readlines():
                    if code.startswith('########'):
                        continue
                    if code.startswith('# create '):
                        continue
                    codes.append(code.rstrip())
        return codes

    def _gen_model_py_code(self,outfile):
        models_class_code = self._get_models_class_code(outfile)
        if not models_class_code:
            models_code = ['from .models_base import *']
        else:
            models_code = models_class_code.copy()
        class_def_lower = [c.lower().split('(')[0]+'(' for c in models_code if c.startswith('class ')]
        for table in self.tables:
            bo_class = table.tablename.capitalize()
            # 继承的类不能在model中再继承定义，否则会不能新增数据
            if table.is_sigletable:
                continue
            bo_class_def = 'class {cls_name}({cls_name}{cls_suffix}):' .format (
                              cls_name =bo_class,
                              cls_suffix=self.class_suffix)
            # 只要包含class的定义即可,小写
            if bo_class_def.split('(')[0].lower()+'(' not in class_def_lower :
                models_code.append(bo_class_def)
                models_code.append('    pass')
        return models_code

    def gen_code(self,outfile,exists2cover=True):
        super().gen_code(outfile)
        import os
        # 创建models.py
        models_code = self._gen_model_py_code(outfile)
        models_file = os.path.join(os.path.dirname(outfile), MODELS_PY)
        saveUTF8File(models_file, models_code)

class BoCodeGenerator_sqlalchemy(BoCodeGenerator_base):
    '''
    创建sqlalchemy 的model
    '''
    def __init__(self,database_dict):
        super().__init__(database_dict)
        # 如：db.Model,db.Column
        self.model_prefix = ''
        # 类的后缀，如_base 。。。
        self.class_suffix = ''
        self.template_file = 'flask_models.pys'

    def __gen_ext_py_code(self):
        codes = []
        codes.append('from sqlalchemy.ext.declarative import declarative_base')
        codes.append('from sqlalchemy import create_engine')
        codes.append('from sqlalchemy.orm import sessionmaker')
        codes.append('Base = declarative_base()')
        codes.append('engine = create_engine("sqlite:///:memory:")')
        codes.append("   ")
        codes.append('Session = sessionmaker(bind=engine)')
        return codes

    def gen_code(self,outfile,exists2cover=False):
        # todo delete exists2cover = True
        # exists2cover = True
        super().gen_code(outfile,exists2cover)
        import os
        # 创建ext.py
        ext_file =os.path.join(os.path.dirname(outfile), 'ext.py')
        if not os.path.exists(ext_file):
            saveUTF8File(ext_file,self.__gen_ext_py_code())

class Gen_bo_models():
    def __init__(self,modelfile,outfile,type='flask'):
        imp = ImportDDModels()
        self.database_dictionary = imp.impUMLModels(modelfile)
        self.outfile= outfile
        if type == Gen_type.flask.value:
            self.bo_code_generator = BoCodeGenerator_flask(self.database_dictionary)
        elif type == Gen_type.sql.value:
            self.bo_code_generator = BoCodeGenerator_sqlalchemy(self.database_dictionary)
        else:
            self.bo_code_generator = BoCodeGenerator_flask(self.database_dictionary)

    def gen_code(self,exists2cover=True):
        self.bo_code_generator.gen_code(self.outfile,exists2cover)








