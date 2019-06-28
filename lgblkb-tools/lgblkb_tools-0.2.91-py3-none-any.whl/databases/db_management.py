from geoalchemy2.shape import to_shape
import functools
import typing
import sqlalchemy.orm.session as orms
from copy import deepcopy
from functools import partial
from contextlib import contextmanager
import sqlalchemy as sa
import sqlalchemy.exc
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from .. import global_support as gsup
from .. import log_support as logsup
from box import Box
from . import sqla_orms
from .utils import get_info

# configs=None
# drivername=None
# default_db_configs=None

# def set_configs(_configs,default: str):
# 	# global configs,drivername,default_db_configs
# 	configs=_configs
# 	default_db_configs=_configs[default]
# 	drivername=_configs.drivername
drivername='postgres'

def get_engine(db_configs: dict,create_if_not_exists=False,**connection_kwargs):
	# db_configs=(db_configs or default_db_configs).copy()
	db_configs=db_configs.copy()
	database=connection_kwargs.pop('database') if connection_kwargs.get('database') else db_configs.pop('database')
	# if connection_kwargs.get('database'): database=connection_kwargs.pop('database')
	# elif db_configs.get('database'): database=db_configs.pop('database')
	engine_creator=lambda db:sa.create_engine(URL(**dict(dict(db_configs,drivername=drivername,database=db),
	                                                     **connection_kwargs)),echo=False)
	
	@logsup.logger.with_logging(log_level=logsup.INFORM)
	def __create_database():
		eng=engine_creator('postgres')
		conn=eng.connect()
		conn.execute('commit')
		conn.execute(f'create database {database};')
		conn.close()
	
	if create_if_not_exists:
		try:
			engine=engine_creator(database)
			engine.connect()
		except sa.exc.OperationalError:
			logsup.logger.inform(f"Database '{database}' does not exist.")
			__create_database()
			engine=engine_creator(database)
	else:
		engine=engine_creator(database)
	engine.connect().execute("create extension if not exists postgis;"
	                         "create extension if not exists postgis_topology;")
	# simple_logger.info('engine: %s',engine)
	return engine

def get_session(engine,autoflush=True,autocommit=False,expire_on_commit=True,info=None,**kwargs) -> orms.Session:
	session=sessionmaker(bind=engine,autoflush=autoflush,autocommit=autocommit,expire_on_commit=expire_on_commit,
	                     info=info,**kwargs)()
	return session

@contextmanager
def session_context(engine,autoflush=True,autocommit=False,expire_on_commit=True,info=None,**kwargs):
	session=get_session(engine,autoflush=autoflush,autocommit=autocommit,expire_on_commit=expire_on_commit,info=info,**kwargs)
	try:
		yield session
		session.commit()
	except Exception as e:
		logsup.logger.inform(str(e),exc_info=True)
		session.rollback()
		raise
	finally:
		session.close()

class QueryItem(sqla_orms.Reconnectable):
	_protected_keys=['info',*['_QueryItem'+x for x in ['__item','__engine_creator','__obj_class','__primary_keys']]]
	
	def __init__(self,obj: sqla_orms.Base,engine_creator,pkeys):
		self.__item=Box(deepcopy(obj.__dict__))
		self.__obj_class=obj.__class__
		self.__engine_creator=engine_creator
		self.__primary_keys=tuple([x for x in pkeys] if type(pkeys[0]) is str else [x.key for x in pkeys])
	
	@property
	def primary_vals(self):
		return tuple(getattr(self.__item,x) for x in self.__primary_keys)
	
	@property
	def info(self):
		return get_info(self.__item)
	
	def reconnect(self,session):
		target_obj=session.query(self.__obj_class).get(self.primary_vals)
		assert target_obj is not None,f"Query on {self.__obj_class} returned None."
		return target_obj
	
	def get_wkt(self,key='geom'):
		return to_shape(self.__item[key]).wkt
	
	def __setattr__(self,key,value):
		if key in self._protected_keys:
			self.__dict__[key]=value
		else:
			with session_context(self.__engine_creator()) as temp_session:
				setattr(self.reconnect(temp_session),key,value)
				self.__item[key]=value
	
	def __repr__(self):
		return f"QueryItem: {gsup.reprer(self.__item)}"
	
	def __getattr__(self,item):
		if item in self._protected_keys:
			return self.__dict__[item]
		return self.__item[item]
	
	def __getstate__(self):
		return self.__dict__
	
	def __setstate__(self,state):
		for k,v in state.items():
			setattr(self,k,v)

class Manager(object):
	_protected_keys=['_Manager'+x for x in ['__engine_creator','__engine','__session','__fire_session',
	                                        '__box','__query_item_creator','__temp_ident']]
	
	def __init__(self,db_configs: dict,create_if_not_exists=False,**connection_kwargs):
		self.__engine_creator=partial(get_engine,db_configs,create_if_not_exists,**connection_kwargs)
		self.__engine=None
		self.__session=None
		self.__query_item_creator=partial(QueryItem,engine_creator=self.__engine_creator)
		self.__box=Box()
		self.__temp_ident=None
	
	@property
	def engine(self):
		if self.__engine is None:
			self.__engine=self.__engine_creator()
		return self.__engine
	
	@property
	def session(self):
		if self.__session is None:
			self.__session=get_session(self.engine)
		return self.__session
	
	def new_session(self,autoflush=True,autocommit=False,expire_on_commit=True,info=None,**kwargs):
		self.__session=session=get_session(self.engine,autoflush=autoflush,autocommit=autocommit,
		                                   expire_on_commit=expire_on_commit,info=info,**kwargs)
		return session
	
	@staticmethod
	def commit_and_close(session):
		session.commit()
		session.close()
	
	def create_table(self,table_class: sqla_orms.Base):
		if self.engine.dialect.has_table(self.engine,table_class.__tablename__):
			logsup.logger.inform(f"Table '{table_class.__tablename__}' already exists.")
		else:
			logsup.logger.inform(f"Creating table '{table_class.__tablename__}'.")
			table_class.__table__.create(self.engine)
		return self
	
	@contextmanager
	def session_context(self,**kwargs):
		self.__session=session=get_session(self.engine,**kwargs)
		try:
			yield session
			session.commit()
		except Exception as e:
			logsup.logger.inform(str(e),exc_info=True)
			session.rollback()
			raise
		finally:
			session.close()
	
	def query_get(self,entity: typing.Type[sqla_orms.KeysBase],*primary_keys):
		assert len(primary_keys)>0,'When querying using query_get, you should provide at least one primary_key.'
		with self.session_context() as session:
			obj=QueryItem(session.query(entity).get(primary_keys),self.__engine_creator,entity.primary_keys)
			return obj
	
	def get_wrapped(self,obj):
		return QueryItem(obj,self.__engine_creator,obj.primary_keys)
	
	def session_wrapper(self,new_engine=True,autoflush=True,autocommit=False,expire_on_commit=True,info=None,**kwargs):
		def wrapper_getter(func):
			@functools.wraps(func)
			def wrapper(*args,**_kwargs):
				has_classarg=gsup.func_has_classarg(func,args)
				if new_engine:
					self.__engine=self.__engine_creator()
				with self.session_context(autoflush=autoflush,autocommit=autocommit,
				                          expire_on_commit=expire_on_commit,info=info,**kwargs) as session:
					if has_classarg:
						result=func(args[0],session,*args[1:],**_kwargs)
					else:
						result=func(session,*args,**_kwargs)
					return result
			
			return wrapper
		
		return wrapper_getter

def main():
	# test_2()
	# test_1()
	# mgr=Manager(host='94.247.135.91',username='docker',password='docker',port='8086')
	# with mgr.session_context():
	# 	a: MainRequest=mgr.session.query(MainRequest).first()
	# 	# print(to_shape(a.cadastre_value))
	# 	print(a.cadastre_value)
	# 	mgr.session.add(SridTest(geom=gmtr.SpatialGeom(to_shape(a.cadastre_value)).convert_crs(4326,3857).geom_obj))
	#
	#
	# return
	# mgr=Manager(host='94.247.135.91',username='docker',password='docker',port='8086')
	
	# s2_info.priority=136
	# print(s2_info)
	
	# mgr.s2_info: Sentinel2_Info=s2_info
	# print(mgr.s2_info.priority)
	# mgr.s2_info.priority=136
	# print(mgr.s2_info.priority)
	# print(mgr.s2_info)
	# s2_info=mgr.session.query(Sentinel2_Info).filter(Sentinel2_Info.priority==36).first()
	pass

if __name__=='__main__':
	main()
