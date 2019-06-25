from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import json
from .ext import Base
from enum import Enum
# Base = declarative_base()

class Relationship_type(Enum):
    o2o = 'one_to_one'
    o2m = 'one_to_many'
    m2o = 'many_to_one'
    m2m = 'many_to_many'

def get_relationship_type(multi1,multi2,navig1,navig2):
    if (multi1 == 1) and (multi2 == 1):
        return Relationship_type.o2o.value
    elif (multi1 == 1 or multi2 == 1) and (multi1 > 1 or multi2 > 1):
        if (navig1 and navig2) \
              or (multi1>multi2 and navig1) \
              or(multi1<multi2 and navig2):
            return Relationship_type.o2m.value
        else:
            return Relationship_type.m2o.value
    elif (multi1 > 1 and multi2 > 1):
        return Relationship_type.m2m.value
    return ''

def new_id():
    from datetime import datetime
    return datetime.today().strftime("%Y%m%d%H%M%S%f")

class Databasedictionary(Base):
    __tablename__ = 'databasedictionary'
    name = Column(String(50))
    description = Column(String(255))
    dbtype = Column(Integer)
    id = Column(String(50), primary_key=True)
    tabledictionarys = relationship("Tabledictionary", backref="databasedictionary",
                                       cascade="all, delete-orphan")

    def __repr__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()}

class Fielddictionary(Base):
    __tablename__ = 'fielddictionary'
    gb32name = Column(String(50))
    doc = Column(String(50))
    repfields = Column(String(50))
    plkfieldpath = Column(String(50))
    plkfieldcode = Column(String(50))
    fieldname = Column(String(50), nullable=False)

    #类图属性名可能同资料库的名称不同
    mapname = Column(String(50))
    fieldsize = Column(Integer)
    englishname = Column(String(50))
    isallownull = Column(Boolean,default=True)
    # TKeyType=(ktUnkown,ktKey,ktForeignKey,ktNotKey,ktsys);
    keytype = Column(Integer)
    fieldtype = Column(String(50))
    big5name = Column(String(50))
    # TFieldFrom=(ffUnknown,ffDatabase,ffLookup,ffCustom);
    fieldfrom = Column(Integer)
    othername = Column(String(50))
    defaultvalue = Column(String(50))
    id = Column(String(50), primary_key=True)
    tabledictionaryid = Column(String(50), ForeignKey("tabledictionary.id"), nullable=False)

    def __repr__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()}


class Roledictionary(Base):
    __tablename__ = 'roledictionary'
    end1_rolename = Column(String(50))
    end1_multiplicity = Column(Integer,default=0)
    end1_navigable = Column(Boolean)
    end1_reftableid   = Column(String(50), ForeignKey("tabledictionary.id"))
    end1_reftable = relationship("Tabledictionary", foreign_keys=[end1_reftableid], uselist=False)
    end1_mapid = Column(String(50))
    end1_aggregation = Column(String(50))
    end2_multiplicity = Column(Integer, default=0)
    end2_navigable = Column(Boolean)
    end2_rolename = Column(String(50))
    end2_reftableid   = Column(String(50), ForeignKey("tabledictionary.id"))
    end2_reftable = relationship("Tabledictionary", foreign_keys=[end2_reftableid], uselist=False)
    end2_mapid = Column(String(50))
    end2_aggregation = Column(String(50))
    # masterdetail = Column(Boolean)
    ref = Column(Boolean)
    req = Column(Boolean)
    # primaryjoin
    flt = Column(String(100))
    # order_by
    ord = Column(String(50))
    ownertableid = Column(String(50), ForeignKey("tabledictionary.id"))
    ownertable = relationship("Tabledictionary", foreign_keys=[ownertableid], backref="roledictionarys")

    # 多对多关联类
    is_assoc_table = Column(Boolean)
    assoc_tableid = Column(String(50), ForeignKey("tabledictionary.id"))
    assoc_table = relationship("Tabledictionary", foreign_keys=[assoc_tableid],uselist=False)

    # refmasterdetail = Column(Boolean)
    id = Column(String(50), primary_key=True)
    # 关联id 是否要加下划线
    underline = Column(Boolean,default=False)
    # 记录database的id，用以区分是哪个资料库
    ddid = Column(String(50))

    @property
    def end1_foreign_key_name(self):
        get_id = lambda underline: '_id' if underline else 'id'
        return (self.end1_rolename + get_id(self.underline)).lower()

    @property
    def end2_foreign_key_name(self):
        get_id = lambda underline: '_id' if underline else 'id'
        return (self.end2_rolename + get_id(self.underline)).lower()

    def __get_relationship_type(self):
        return get_relationship_type(self.end1_multiplicity, self.end2_multiplicity,
                                     self.end1_navigable, self.end2_navigable)
    # 是一对一关系，做双向
    def is_o2o(self):
        return self.__get_relationship_type()==Relationship_type.o2o.value
    # 多对一关系，只处理单向，当lookup关系
    def is_m2o(self):
        return self.__get_relationship_type()==Relationship_type.m2o.value
    # 一对多,做双向
    def is_o2m(self):
        return self.__get_relationship_type()==Relationship_type.o2m.value

    # 多对多
    def is_m2m(self):
        return self.__get_relationship_type() == Relationship_type.m2m.value

    # master-detail关系
    def is_md(self):
        return (self.end1_aggregation == 'composite' or
                self.end2_aggregation == 'composite')\
               and self.is_o2m()

    # 自引用
    def is_tree(self):
        return (self.end1_reftableid== self.end2_reftableid)or\
               (self.end1_reftable.is_sigletable and self.end2_reftable.is_sigletable and
                self.end1_reftable.parentid==self.end2_reftable.id
                )

    def __repr__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()}

class Tabledictionary(Base):
    __tablename__ = 'tabledictionary'
    # viewsql = Column(String(2048))
    id = Column(String(50), primary_key=True)
    databasedictionaryid = Column(String(50), ForeignKey("databasedictionary.id"), nullable=False)
    tablename = Column(String(50), nullable=False, unique=True)
    maptablename = Column(String(50))
    description = Column(String(250))
    fielddictionarys = relationship("Fielddictionary", backref="tabledictionary",
                                        cascade="all, delete-orphan")
    ddoperations = relationship("Ddoperation", backref="parent",
                                        cascade="all, delete-orphan")
    # 是父类
    is_parentclass = Column(Boolean,default=False)

    # 儿子类有parent
    parentid = Column(String(50),ForeignKey("tabledictionary.id"))
    parent = relationship("Tabledictionary", foreign_keys="Tabledictionary.parentid", remote_side=[id])
    # 继承关系只有一个table
    is_sigletable = Column(Boolean,default=False)
    # 是多对多关联类
    is_assoc_table = Column(Boolean)
    # 抽象类
    isabstract = Column(Boolean, default=False)

    def get_keyfield(self):
        for fld in self.fielddictionarys:
            if fld.keytype==1:
                return fld
        return None

    def __repr__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()}


class Ddoperation(Base):
    __tablename__ = 'ddoperation'
    id = Column(String(50), primary_key=True)
    name = Column(String(50))
    stereotype = Column(String(50))
    doc = Column(String(50))
    py_params = Column(String(50))
    specification = Column(String(500))
    isabstract = Column(Boolean, default= False)
    isquery = Column(Boolean, default= False)
    isstatic = Column(Boolean, default= False)
    parentid = Column(String(50),ForeignKey("tabledictionary.id"), nullable= False)
    # parent = relationship("Tabledictionary", back_populates="ddoperations", foreign_keys="Ddoperation.parentid")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }


class DBEnumeration(Base):
    __tablename__ = "dbenumeration"
    name = Column(String(50))
    # 支持string，integer，boolean
    type = Column(String(50))
    doc = Column(String(50))
    # 关联类的关联
    enumeitems = relationship("DBEnumeitem")
    id = Column(String(50), primary_key=True)
    # 记录database的id，用以区分专案
    ddid = Column(String(50))
    def __repr__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()}

class DBEnumeitem(Base):
    __tablename__ = "dbenumeitem"
    name = Column(String(50))
    type = Column(String(50))
    value = Column(String(50))
    doc = Column(String(50))
    id = Column(String(50), primary_key=True)
    enumerationid = Column(String(50), ForeignKey("dbenumeration.id"))

    def __repr__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()}
