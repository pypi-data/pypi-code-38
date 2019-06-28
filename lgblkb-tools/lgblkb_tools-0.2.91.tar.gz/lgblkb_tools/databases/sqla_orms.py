import os
import joblib
from typing import Union,Type
from abc import abstractmethod
import geoalchemy2 as ga
import sqlalchemy as sa
from sqlalchemy import Column,TIMESTAMP,Integer,Text,ARRAY,sql,REAL,ForeignKey,VARCHAR,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,backref
from sqlalchemy.schema import UniqueConstraint
from ..global_support import reprer
from .statuses import image_status
from .utils import get_info
from ..folder_utils import Folder
from .. import log_support as logsup

Base=declarative_base()

class InfoBase(object):
	
	@property
	def info(self):
		return get_info(self)
	
	def __repr__(self):
		return reprer(self)

# def info(self):
# 	return mgr.get_wrapped(self)

class StatusTrackable(InfoBase):
	status_key='status'

class Reconnectable(InfoBase):
	
	@abstractmethod
	def reconnect(self,session):
		pass
	
	@staticmethod
	def get_dump_filepath(folder=None,filename='',filepath=''):
		if not filepath:
			assert all([folder,filename]),'Dump folder and filename should be provided.'
			filepath=Folder(folder).get_filepath(filename)
			if not os.path.splitext(filepath)[-1]: filepath+='.joblib'
		logsup.logger.debug('filepath: %s',filepath)
		return filepath
	
	@classmethod
	def from_dump(cls,folder=None,filename='',filepath=''):
		filepath=cls.get_dump_filepath(folder=folder,filename=filename,filepath=filepath)
		assert os.path.exists(filepath),f'Filepath {filepath} does not exist.'
		logsup.logger.debug('Loading object from dump file.')
		return joblib.load(filepath)
	
	def to_dump(self,folder=None,filename='',filepath=''):
		filepath=self.get_dump_filepath(folder=folder,filename=filename,filepath=filepath)
		joblib.dump(self,filepath)
		return self
	
	

class KeysBase(Reconnectable):
	primary_keys=['id']
	
	def reconnect(self,session):
		pass
	
	def __repr__(self):
		return reprer(self)

class IntegerID_Base(KeysBase):
	id=Column(Integer,primary_key=True)

class TextID_Base(KeysBase):
	id=Column(Text,primary_key=True)

class SnowTest(Base,IntegerID_Base):
	__tablename__='snow_test'
	geom=Column(ga.Geometry('MULTIPOLYGON'))

class Cadastres_Info(Base,IntegerID_Base):
	__tablename__='cadastres_cadastre'
	kad_nomer=Column(Text)
	area=Column(REAL)
	geom=Column(ga.Geometry('MULTIPOLYGON',srid=3857))
	is_custom=Column(Boolean)

class Test_Srid(Base,IntegerID_Base):
	__tablename__='test_srid'
	ball_b=Column(REAL)
	descr=Column(Text)
	legend=Column(Text)
	geometry=Column(ga.Geometry(srid=3857))
	kad_nomer=Column(VARCHAR(20))
	area=Column(REAL)

class Test_Vectors(Base,IntegerID_Base):
	__tablename__='test_vectors'
	geometry=Column(ga.Geometry(srid=3857))
	index_value=Column(REAL)

# class Cadastres_Info2(Base,IntegerID_Base):
# 	__tablename__='cadastres_cadastre2'
# 	kad_nomer=Column(Text)
# 	area=Column(REAL)
# 	geom=Column(ga.Geometry('MULTIPOLYGON'))

class MainRequest(Base,IntegerID_Base,StatusTrackable):
	status_key='back_status'
	__tablename__='main_requests_request'
	request_date=Column(TIMESTAMP(True),server_default=sql.func.now())
	image_date=Column(TIMESTAMP(True),server_default=None)
	user_id=Column(Integer)
	order_request_date=Column(sa.Date,server_default=None)
	cadastre_id=Column(Integer)
	cadastre_value=Column(ga.Geometry('MULTIPOLYGON'))
	status=Column(Integer)
	status_changer=Column(Integer,default=0)
	back_status=Column(Text,default=image_status.Unprocessed)
	last_lookup_date=Column(TIMESTAMP(True),server_default=None)
	product_ids=Column(ARRAY(Text),server_default=None)
	results_dir=Column(Text,server_default=None)
	priority=Column(Integer,default=5)

class ImageDateChecker(Base,IntegerID_Base,StatusTrackable):
	status_key='image_date_checker_status'
	__tablename__='main_requests_imagedate'
	image_date=Column(TIMESTAMP(timezone=True))
	request_id=Column(Integer,ForeignKey(f'{MainRequest.__tablename__}.id'))
	cadastre_value=Column(ga.Geometry('MULTIPOLYGON'))
	image_date_checker_status=Column(Text)
	priority=Column(Integer,default=5)
	
	backend_request=relationship(MainRequest,uselist=False,backref=backref('image_date_request',cascade='all,delete'))

class User(Base,IntegerID_Base):
	__tablename__='auth_user'
	password=Column(sa.VARCHAR(128))
	last_login=Column(TIMESTAMP(timezone=True))
	is_superuser=Column(sa.Boolean,server_default='f')
	username=Column(sa.VARCHAR(150))
	first_name=Column(sa.VARCHAR(30))
	last_name=Column(sa.VARCHAR(150))
	email=Column(sa.VARCHAR(254))
	is_staff=Column(sa.Boolean,server_default='f')
	is_active=Column(sa.Boolean,server_default='t')
	date_joined=Column(TIMESTAMP(timezone=True))

class MeteoData(Base,KeysBase):
	__tablename__='meteo_data_2'
	primary_keys=['geometry','forecast_date']
	geometry=Column(ga.Geometry('POINT'),primary_key=True)
	forecast_date=Column(TIMESTAMP(timezone=True),primary_key=True)
	__table_args__=(UniqueConstraint('geometry','forecast_date'),)

class Sentinel2_Info(TextID_Base,Base,StatusTrackable):
	__tablename__='sentinel2_info'
	image_date=Column(TIMESTAMP(timezone=True))
	download_date=Column(TIMESTAMP(timezone=True))
	product_path_l1c=Column(Text,server_default=None)
	zip_path=Column(Text)
	product_path_l2a=Column(Text,server_default=None)
	status=Column(Text,server_default=image_status.Unprocessed)
	priority=Column(Integer,default=5)

class CeleryInfo(Base,IntegerID_Base):
	__tablename__='celery_taskmeta'
	task_id=Column(VARCHAR(155))
	status=Column(VARCHAR(50))
	date_done=Column(TIMESTAMP(True))
	traceback=Column(Text)
	
	def __repr__(self):
		return reprer(self)

class CadastreUser(Base,IntegerID_Base):
	__tablename__='cadastres_cadastreuser'
	
	title=Column(Text)
	cadastre_id=Column(Integer)
	user_id=Column(Integer)

def main():
	# Sentinel2_Info.__table__.create(engine)
	pass
	# old_statuses=collections.OrderedDict()
	# old_statuses['RunningAtmosphericCorrection']=image_status.Running.AtmosphericCorrection
	# old_statuses['FinishedAtmosphericCorrection']=image_status.Finished.AtmosphericCorrection
	# old_statuses['QueuedForAtmosphericCorrection']=image_status.QueuedFor.AtmosphericCorrection
	# old_statuses['NotForProcessing']=image_status.NotForProcessing
	#
	# for old_status,new_status in old_statuses.items():
	# 	for row in session.query(Sentinel2_Info).filter(Sentinel2_Info.status==old_status).all():
	# 		row.status=new_status
	pass
	
	pass

if __name__=='__main__':
	main()
