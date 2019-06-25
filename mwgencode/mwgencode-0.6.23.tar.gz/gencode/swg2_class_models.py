########################################
# create by :cxh-pc
# create time :2018-04-26 20:44:57.895581
########################################
from sqlalchemy import Table,Column, Integer, String, ForeignKey, Boolean,\
                DateTime,Time,Date,Float
from sqlalchemy.orm import relationship,aliased
from sqlalchemy import or_
from .ext import Base as Model
import json
from enum import Enum
class Swagger2(Model):
    __tablename__ = 'swagger2'
    name = Column(String(50), unique= True)
    host = Column(String(50))
    version = Column(String(50))
    id = Column(String(50), primary_key=True)
    resp_xml = Column(Boolean)
    doc = Column(String(50))
    auth = Column(String(50), default= "jwt")
    tags = relationship("Tag2", back_populates="swagger", foreign_keys="Tag2.swaggerid", cascade="all, delete-orphan")
    defines = relationship("Define2", back_populates="swagger", foreign_keys="Define2.swaggerid", cascade="all, delete-orphan")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Tag2(Model):
    __tablename__ = 'tag2'
    name = Column(String(50), unique= True)
    doc = Column(String(50))
    id = Column(String(50), primary_key=True)
    swaggerid = Column(String(50),ForeignKey("swagger2.id"), nullable= False)
    swagger = relationship("Swagger2", back_populates="tags", foreign_keys="Tag2.swaggerid")
    paths = relationship("Path2", back_populates="tag", foreign_keys="Path2.tagid", cascade="all, delete-orphan")
    def call_path(self):
        return self.name
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Action2(Model):
    """
    把path归于tag下，更易于产生代码
    """
    __tablename__ = 'action2'
    action = Column(String(50))
    summary = Column(String(50))
    doc = Column(String(50))
    ver_str = Column(String(50))
    has_formdata = Column(Boolean)
    id = Column(String(50), primary_key=True)
    is_lk = Column(Boolean, default= False)
    # stereotype 包含 lk ，如：get/lk
    include_lk = Column(Boolean, default= False)
    # 有page过滤条件
    has_page = Column(Boolean, default= False)
    in_param_name = Column(String(50))
    return_param_name = Column(String(50))
    # 需要认证
    is_auth = Column(Boolean, default= False)
    pathid = Column(Integer,ForeignKey("path2.id"), nullable= False)
    default_respid = Column(Integer,ForeignKey("resp2.id"))
    path = relationship("Path2", back_populates="actions", foreign_keys="Action2.pathid")
    default_resp = relationship("Resp2", foreign_keys="Action2.default_respid")
    params = relationship("Param2", back_populates="action", foreign_keys="Param2.actionid", cascade="all, delete-orphan")
    resps = relationship("Resp2", back_populates="action", foreign_keys="Resp2.actionid", cascade="all, delete-orphan")
    def call_path(self):
        return '%s.%s'%(self.path.call_path(),self.action)
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Param2(Model):
    __tablename__ = 'param2'
    in_ = Column(String(50))
    name = Column(String(50))
    desc = Column(String(50))
    required = Column(Boolean)
    is_array = Column(Boolean)
    type_attr = Column(String(50))
    type = Column(String(50))
    format = Column(String(50))
    ref_name = Column(String(50))
    id = Column(Integer, primary_key=True)
    is_path = Column(Boolean, default= False)
    is_header = Column(Boolean, default= False)
    is_body = Column(Boolean, default= False)
    is_query = Column(Boolean, default= False)
    is_formdata = Column(Boolean, default= False)
    actionid = Column(String(50),ForeignKey("action2.id"), nullable= False)
    action = relationship("Action2", back_populates="params", foreign_keys="Param2.actionid")
    def call_path(self):
        return '%s.%s'%(self.action.call_path(),self.name)
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Resp2(Model):
    __tablename__ = 'resp2'
    code = Column(String(50))
    desc = Column(String(50))
    type_attr = Column(String(50))
    is_array = Column(Boolean)
    ref_name = Column(String(50), default= '')
    type = Column(String(50))
    id = Column(Integer, primary_key=True)
    format = Column(String(50))
    # 记录引用物件的类型
    umlcls_type = Column(String(50))
    name = Column(String(50), default= '')
    actionid = Column(String(50),ForeignKey("action2.id"), nullable= False)
    action = relationship("Action2", back_populates="resps", foreign_keys="Resp2.actionid")
    def call_path(self):
        return '%s.%s'%(self.action.call_path(),self.name)
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Define2(Model):
    __tablename__ = 'define2'
    name = Column(String(50), unique= True)
    desc = Column(String(50))
    id = Column(String(50), primary_key=True)
    is_lk = Column(Boolean, default= False)
    swaggerid = Column(String(50),ForeignKey("swagger2.id"), nullable= False)
    swagger = relationship("Swagger2", back_populates="defines", foreign_keys="Define2.swaggerid")
    attrs = relationship("Attr2", back_populates="define", foreign_keys="Attr2.defineid", cascade="all, delete-orphan")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Attr2(Model):
    __tablename__ = 'attr2'
    name = Column(String(50))
    is_array = Column(Boolean)
    desc = Column(String(50))
    type_attr = Column(String(50))
    type = Column(String(50))
    format = Column(String(50))
    id = Column(Integer, primary_key=True)
    ref_name = Column(String(50))
    defineid = Column(String(50),ForeignKey("define2.id"), nullable= False)
    define = relationship("Define2", back_populates="attrs", foreign_keys="Attr2.defineid")
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
class Path2(Model):
    __tablename__ = 'path2'
    name = Column(String(50))
    id = Column(Integer, primary_key=True)
    is_lk = Column(Boolean, default= False)
    tagid = Column(String(50),ForeignKey("tag2.id"), nullable= False)
    tag = relationship("Tag2", back_populates="paths", foreign_keys="Path2.tagid")
    actions = relationship("Action2", back_populates="path", foreign_keys="Action2.pathid", cascade="all, delete-orphan")
    def call_path(self):
        return '%s.%s'%(self.tag.call_path(),self.name)
    def __repr__(self):
        return json.dumps(self.to_json())
    def to_json(self):
        return {key: getattr(self, key) for key in self.__table__.columns.keys()
                   if hasattr(self,key)
               }
