########################################
# create by :cxh-pc
# create time :2018-04-26 20:44:58.281737
########################################
from sqlalchemy import Table,Column, Integer, String, ForeignKey, Boolean,\
                DateTime,Time,Date,Float
from sqlalchemy.orm import relationship,aliased
from sqlalchemy import or_
from .ext import Base as Model
import json
from enum import Enum
class Class_uml(Enum):
    umlclass ="UMLClass"
    umlsignal ="UMLSignal"
    umlprimitivetype ="UMLPrimitiveType"
    umldatatype ="UMLDataType"
class Package(Model):
    __tablename__ = 'package'
    name = Column(String(50))
    stereotype = Column(String(50))
    doc = Column(String(50))
    # UMLModel
    type = Column(String(50))
    id = Column(String(50), primary_key=True)
    isswagger = Column(Boolean, default= False)
    parentid = Column(String(50),ForeignKey("package.id"))
    projectid = Column(String(50),ForeignKey("project.id"), nullable= False)
    packages = relationship("Package", back_populates="parent", foreign_keys="Package.parentid", lazy="dynamic")
    parent = relationship("Package", back_populates="packages", foreign_keys="Package.parentid", remote_side=[id])
    project = relationship("Project", back_populates="packages", foreign_keys="Package.projectid")
    diagrams = relationship("Diagram", back_populates="parent", foreign_keys="Diagram.parentid", cascade="all, delete-orphan")
    classs = relationship("Class", back_populates="parent", foreign_keys="Class.parentid", cascade="all, delete-orphan")
    enumerations = relationship("Enumeration", back_populates="package", foreign_keys="Enumeration.packageid", cascade="all, delete-orphan")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Diagram(Model):
    __tablename__ = 'diagram'
    name = Column(String(50))
    isdefault = Column(Boolean, default= False)
    id = Column(String(50), primary_key=True)
    type = Column(String(50))
    isswagger = Column(Boolean, default= False)
    parentid = Column(String(50),ForeignKey("package.id"), nullable= False)
    parent = relationship("Package", back_populates="diagrams", foreign_keys="Diagram.parentid")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Class(Model):
    __tablename__ = 'class'
    name = Column(String(50))
    stereotype = Column(String(50))
    doc = Column(String(50))
    isabstract = Column(Boolean, default= False)
    id = Column(String(50), primary_key=True)
    isswagger = Column(Boolean, default= False)
    type = Column(String(50))
    is_assoc_class = Column(Boolean, default= False)
    projectid = Column(String(50))
    parentid = Column(String(50),ForeignKey("package.id"), nullable= False)
    association_id = Column(String(50),ForeignKey("association.id"))
    parent = relationship("Package", back_populates="classs", foreign_keys="Class.parentid")
    association = relationship("Association", foreign_keys="Class.association_id")
    propertys = relationship("Property", back_populates="parent", foreign_keys="Property.parentid", cascade="all, delete-orphan")
    associations = relationship("Association", back_populates="parent", foreign_keys="Association.parentid", cascade="all, delete-orphan")
    operations = relationship("Operation", back_populates="parent", foreign_keys="Operation.parentid", cascade="all, delete-orphan")
    umlgeneralizations = relationship("Umlgeneralization", back_populates="parent", foreign_keys="Umlgeneralization.parentid", cascade="all, delete-orphan")
    def assign_propertys(self,session):
        if self.type != Class_uml.umlclass.value:
            return
        def assign_assoc_id(cls):
            Assoc_end1 = aliased(Assoc_end)
            Assoc_end2 = aliased(Assoc_end)
            associations = session.query(Association).\
                           join(Assoc_end1,Assoc_end1.id==Association.end1id).\
                           join(Assoc_end2,Assoc_end2.id==Association.end2id).\
                           filter(or_(Assoc_end1.referenceid==cls.id,Assoc_end2.referenceid==cls.id)). \
                       distinct().all()
            get_name = lambda end:end.name.lower() if end.name else end.reference.name.lower()
            for assoc in associations:
                end = assoc.end1
                if end.referenceid==cls.id:
                    end = assoc.end2
                if end.navigable and end.multiplicity.split('..')[-1]=='1':
                    if '_id' in assoc.stereotype.split('/'):
                        id = '_id'
                    else:
                        id = 'id'
                    assoc_id = None
                    for pro in end.reference.propertys:
                        if pro.name=='id':
                            assoc_id = Property(**pro.to_json())
                            assoc_id.name = get_name(end)+id
                            # 不能用cls的name，因为cls可能是target，这样会id重复
                            assoc_id.id = '%s_%s'%(self.name,end.id)
                            break
                    if assoc_id is None:
                        assoc_id = Property(id='%s_%s'%(self.name,end.id),
                                            name=get_name(end)+'id',
                                            type='integer')
                    self.propertys.append(assoc_id)
        for gen in self.umlgeneralizations:
            for property in gen.target.propertys:
                pro = Property(**property.to_json())
                pro.id='%s_%s'%(self.name,pro.id)
                self.propertys.append(pro)
            assign_assoc_id(gen.target)
        assign_assoc_id(self)
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Property(Model):
    __tablename__ = 'property'
    name = Column(String(50))
    stereotype = Column(String(50))
    doc = Column(String(50))
    type = Column(String(50))
    multiplicity = Column(String(50))
    isreadonly = Column(Boolean, default= False)
    isordered = Column(Boolean, default= False)
    isunique = Column(Boolean, default= False)
    defaultvalue = Column(String(50), default= '')
    isid = Column(Boolean, default= False)
    id = Column(String(50), primary_key=True)
    isswagger = Column(Boolean, default= False)
    parentid = Column(String(50),ForeignKey("class.id"), nullable= False)
    objectid = Column(String(50),ForeignKey("class.id"))
    parent = relationship("Class", back_populates="propertys", foreign_keys="Property.parentid")
    object = relationship("Class", foreign_keys="Property.objectid")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Association(Model):
    __tablename__ = 'association'
    id = Column(String(50), primary_key=True)
    name = Column(String(50))
    stereotype = Column(String(50))
    doc = Column(String(50))
    isswagger = Column(Boolean, default= False)
    is_assoc_class = Column(Boolean, default= False)
    projectid = Column(String(50))
    parentid = Column(String(50),ForeignKey("class.id"), nullable= False)
    end1id = Column(String(50),ForeignKey("assoc_end.id"), nullable= False)
    end2id = Column(String(50),ForeignKey("assoc_end.id"), nullable= False)
    assoc_class_id = Column(String(50),ForeignKey("class.id"))
    parent = relationship("Class", back_populates="associations", foreign_keys="Association.parentid")
    end1 = relationship("Assoc_end", foreign_keys="Association.end1id")
    end2 = relationship("Assoc_end", foreign_keys="Association.end2id")
    assoc_class = relationship("Class", foreign_keys="Association.assoc_class_id")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Assoc_end(Model):
    __tablename__ = 'assoc_end'
    id = Column(String(50), primary_key=True)
    name = Column(String(50))
    stereotype = Column(String(50))
    navigable = Column(Boolean)
    aggregation = Column(String(50))
    multiplicity = Column(String(50))
    isswagger = Column(Boolean, default= False)
    isderived = Column(Boolean, default= False)
    referenceid = Column(String(50),ForeignKey("class.id"))
    reference = relationship("Class", foreign_keys="Assoc_end.referenceid")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Project(Model):
    __tablename__ = 'project'
    id = Column(String(50), primary_key=True)
    author = Column(String(50))
    version = Column(String(50))
    doc = Column(String(50))
    isswagger = Column(Boolean, default= False)
    name = Column(String(50))
    # 增加一个flag，确保id不重复，解决文件拷贝导致id重复的问题
    flag = Column(String(50))
    file_name = Column(String(200))
    packages = relationship("Package", back_populates="project", foreign_keys="Package.projectid", cascade="all, delete-orphan")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Operation(Model):
    __tablename__ = 'operation'
    isswagger = Column(Boolean, default= False)
    id = Column(String(50), primary_key=True)
    name = Column(String(50))
    stereotype = Column(String(50))
    doc = Column(String(50))
    # python function的参数定义
    py_params = Column(String(50))
    # 代码内容
    specification = Column(String(500))
    isabstract = Column(Boolean, default= False)
    isquery = Column(Boolean, default= False)
    isstatic = Column(Boolean, default= False)
    in_param_id = Column(String(50),ForeignKey("parameter.id"), nullable= False)
    return_param_id = Column(String(50),ForeignKey("parameter.id"), nullable= False)
    parentid = Column(String(50),ForeignKey("class.id"), nullable= False)
    in_param = relationship("Parameter", foreign_keys="Operation.in_param_id")
    return_param = relationship("Parameter", foreign_keys="Operation.return_param_id")
    parent = relationship("Class", back_populates="operations", foreign_keys="Operation.parentid")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Parameter(Model):
    __tablename__ = 'parameter'
    isswagger = Column(Boolean, default= False)
    id = Column(String(50), primary_key=True)
    name = Column(String(50))
    stereotype = Column(String(50))
    type = Column(String(50))
    multiplicity = Column(String(50))
    object_type_id = Column(String(50),ForeignKey("class.id"))
    object_type = relationship("Class", foreign_keys="Parameter.object_type_id")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Enumeration(Model):
    __tablename__ = 'enumeration'
    name = Column(String(50))
    id = Column(String(50), primary_key=True)
    doc = Column(String(50))
    stereotype = Column(String(50))
    isswagger = Column(Boolean, default= False)
    projectid = Column(String(50))
    packageid = Column(String(50),ForeignKey("package.id"), nullable= False)
    package = relationship("Package", back_populates="enumerations", foreign_keys="Enumeration.packageid")
    enumeitems = relationship("Enumeitem", back_populates="enumeration", foreign_keys="Enumeitem.enumerationid", cascade="all, delete-orphan")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Enumeitem(Model):
    __tablename__ = 'enumeitem'
    name = Column(String(50))
    stereotype = Column(String(50))
    doc = Column(String(50))
    id = Column(String(50), primary_key=True)
    isswagger = Column(Boolean, default= False)
    enumerationid = Column(String(50),ForeignKey("enumeration.id"), nullable= False)
    enumeration = relationship("Enumeration", back_populates="enumeitems", foreign_keys="Enumeitem.enumerationid")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Umlgeneralization(Model):
    __tablename__ = 'umlgeneralization'
    discriminator = Column(String(50))
    stereotype = Column(String(50))
    isswagger = Column(Boolean, default= False)
    id = Column(String(50), nullable= False, primary_key=True)
    sourceid = Column(String(50),ForeignKey("class.id"), nullable= False)
    targetid = Column(String(50),ForeignKey("class.id"), nullable= False)
    parentid = Column(String(50),ForeignKey("class.id"), nullable= False)
    source = relationship("Class", foreign_keys="Umlgeneralization.sourceid")
    target = relationship("Class", foreign_keys="Umlgeneralization.targetid")
    parent = relationship("Class", back_populates="umlgeneralizations", foreign_keys="Umlgeneralization.parentid")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
