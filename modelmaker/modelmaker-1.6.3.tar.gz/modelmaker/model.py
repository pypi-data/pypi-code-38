import time,sys
import os
from datetime import datetime, timedelta
from .client.api import *
from .predictor import *
#============================
import json
import logging
from six import with_metaclass
from abc import ABCMeta, abstractmethod
from json import JSONEncoder

logging.basicConfig()
LOGGER = logging.getLogger('modelmaker-sdk/Model')
LOGGER_LEVEL = os.getenv("MODELMAKER_LEVEL", logging.INFO) #cloud
LOGGER.setLevel(int(LOGGER_LEVEL))

ISOTIMEFORMAT = '%m%d-%H%M%S'
CREATE_MODEL_PARAMS = set(['model_name', 'model_version', 'model_path',
						   'model_framework', 'model_framework_type', 'model_code_dir',
						   'model_boot_file', 'model_call_specs', 'model_description','model_mirrorUrl','model_id','model_git_info'])
DEPLOY_SERVICE_PARAMS = set(['service_name', 'service_type', 'service_models'])
DEPLOY_SERVICE_MODELS_PARAMS = set(['modelVersionId', 'weight', 'resourceId', 'instanceCount','envs'])

MODEL_WAIT_SECOND = 5
MAXIMUM_RETRY_TIMES = 200000


class Model(object):
	"""
	A ModelMaker Model that can be created model, deployed model service,
	got model info and list, and deleted model and service endpoint.
	"""
	def __init__(self, session):
		"""
		Initialize a model, determine the model authorize type.
		param session: Building interactions with Wangsu Cloud service.
		"""
		self.session = session
		self.service_id = None
		self.model_id	= None
		self.model_version_id = None
		self.model_instance = ModelApiAccountImpl(self.session)

	def create_model(self, **kwargs):
		""" creating model interface
		Args:
			kwargs: Create model body params
		Returns:
			dict: model_id that creating successfully
		"""
		self.model_instance.check_params(1,**kwargs)
		model_create_resp = self.model_instance.create_modelmaker_model(kwargs['model_name'])
		self.model_id = self.model_instance.model_id
		self.model_version_id = self.model_instance.model_version_id
		return json.loads(model_create_resp.data.decode('utf-8'))

	def deploy_predictor(self, **kwargs):
		""" Deploying model predictor interface
			Args:
				kwargs: Deploying predictor body params
			Returns:
				dict: service_id that creating successfully
		"""
		self.model_instance.check_params(2,**kwargs)
		model_deploy_resp = self.model_instance.deploy_modelmaker_predictor()
		self.service_id   = self.model_instance.service_id
		return model_deploy_resp

	def model_info(self, model_id=None):
		"""
		return model information list of the input model_id or the last created model
		"""
		result  = self.model_instance.get_model_info(model_id=model_id)
		result  = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	def get_model_version_info(self, model_version_id=None):
		"""
		return model information list of the input model_id or the last created model
		"""
		result  = self.model_instance.get_model_version_info(model_version_id=model_version_id)
		result  = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	def preset_model(self):

		result = self.model_instance.get_preset_model()
		result  = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	def predict_machine(self):

		result = self.model_instance.get_predict_instance_types()
		result  = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	def predict_framework(self):

		result = self.model_instance.get_predict_framework_list()
		result  = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	def destory_model(self, model_id = None):

		result = self.model_instance.delete_model(model_id = model_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))

	def destory_model_version(self, model_version_id = None):
		
		result  = self.model_instance.delete_model_version(model_version_id = model_version_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))

	def delete_model(self, model_version_id = None):
		
		result  = self.model_instance.delete_model_version(model_version_id = model_version_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))

#	def delete_model_endpoint(self, model_id=None, service_id=None):
#
#		self.model_instance.delete_model_endpoint(model_id=model_id, service_id=service_id)

	def delete_service(self, service_id=None):

		result = self.model_instance.delete_service(service_id = service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))

	def get_service_id(self):

		return LOGGER.info(self.service_id)

	def get_model_version_id(self):

		return LOGGER.info(self.model_version_id)


	def get_model_id(self):

		return LOGGER.info(self.model_id)

class ModelApiBase(with_metaclass(ABCMeta, object)):
	""" A ModelMaker Model that can be created model, deployed model service and delete model endpoint. """

	def __init__(self):

		"""
		Initialize a ModelMaker Model instance.
		"""
	@classmethod
	def s3_user_code_upload(cls,session,path):
		if path is None:
			return path
		elif isinstance(path,str):
			if path.startswith("s3://") == True:
				return path
			else:
				if path[-1] == "/":
					path = path[:-1]
				if session.bucket == None:
					raise Exception("Session(...,bucket=xxx) must be set!")
				if not os.path.exists(path):
					raise Exception("Path " + path + " does not exist!")
				else:
					if hasattr(cls,'s3_path'):
						pass
					else:
						beijing_date = (datetime.now()+ timedelta(hours=8)).strftime(ISOTIMEFORMAT)
						session.create_directory(session.bucket,beijing_date)
						cls.s3_path = os.path.join(session.bucket, beijing_date)
					session.upload_data(cls.s3_path + '/',path)
					if os.path.isdir(path):
						result = "s3://"+ os.path.join(cls.s3_path, path.split('/')[-1]) + "/"
					else:
						result = "s3://"+ cls.s3_path + "/"
					LOGGER.info("Success upload %s to %s!"%(path, result))
					return result
		else:
			raise TypeError("code_dir must be string !!")

	def check_params(self, flag, **kwargs):
		""" Checking the model parameters validity from console
		 Args:
			 kwargs(dict): creating model parameters or deploying service parameters
		"""
		if flag == 1:
			Framework_type = ["BASIC_FRAMEWORK","PRESET_MODEL","CUSTOM"]
			config_set = set(kwargs.keys()) - CREATE_MODEL_PARAMS
			if len(config_set) == 0:
				if kwargs['model_framework_type'] == None or kwargs['model_framework_type'] not in Framework_type:
					raise ValueError('framework_type is must setted in "BASIC_FRAMEWORK","PRESET_MODEL","CUSTOM" ')
				else:
					self._generate_model_params(model_params=kwargs)
			else:
				raise ValueError('The input params: %s for creating model is surplus' % config_set)
		elif flag == 2:
			service_input = set(kwargs.keys())
			if service_input == DEPLOY_SERVICE_PARAMS:
					service_models_input = set(kwargs['service_models'][0].keys())
					if 'weight' in service_models_input and 'resourceId' in service_models_input and 'instanceCount' in service_models_input:

						if 'modelVersionId' not in service_models_input and self.model_version_id:
								kwargs['service_models'][0]['modelVersionId'] = self.model_version_id
								self._generate_service_params(service_params=kwargs)
						elif 'modelVersionId' in service_models_input and self.model_version_id:
								tmp_model_version_id = kwargs['service_models'][0]['modelVersionId']
								if tmp_model_version_id == self.model_version_id:
									self._generate_service_params(service_params=kwargs)
								else:
									LOGGER.warning("Current model_version_id %s, bug it will create model by model_version_id :%s"%(str(self.model_version_id),tmp_model_version_id))
									self._generate_service_params(service_params=kwargs)
						elif 'modelVersionId' in service_models_input and self.model_version_id is None:
								self._generate_service_params(service_params=kwargs)
						else:
							raise ValueError('Please use create_model first, or input parameter service_models=[{modelVersionId:]}')
					else:
						raise ValueError('The input parameter at least require %s' % 'weight/resourceId/instanceCount')
			else:
				raise ValueError('The input parameter require %s' % DEPLOY_SERVICE_PARAMS)

	def _generate_model_params(self, model_params):
		""" Processing and generating the model create parameters:
			[model_name, model_version, source_location, model_type, execution_code]

			Args:
				model_params: the model parameters
		"""
		_config = {}
		if model_params['model_framework_type'] == "BASIC_FRAMEWORK":
			if model_params.get('model_name') and model_params.get('model_framework_type') and model_params.get('model_version') \
							and model_params.get('model_framework') and model_params.get('model_path') and (model_params.get('model_code_dir') or model_params.get('model_git_info')):

				_config['name'] = model_params['model_name']
				_config['type'] = model_params['model_framework_type']
				_config['version'] = model_params['model_version']
				_config['frameworkId'] = model_params['model_framework']
				_config['modelPath'] = model_params['model_path']
				result = self.get_predict_framework_list()
				result = json.loads(result.data.decode('utf-8'))
				frameworkId_list = [ item['id'] for item in result['frameWorks']]
				if _config['frameworkId'] not in frameworkId_list:
					raise ValueError("model_framwork is not exist, please check it!")
				if 'model_code_dir' in model_params:
					_config['codeUrl'] = ModelApiBase.s3_user_code_upload(self.session, model_params['model_code_dir'])
				if 'model_git_info' in model_params:
					_config['gitInfo'] = model_params['model_git_info']
				if 'model_boot_file' in model_params:
					_config['startup'] = model_params['model_boot_file']
				if 'model_call_specs' in model_params:
					_config['callSpecs'] = model_params['model_call_specs']
			else:
				raise ValueError("when model_framework_type = BASIC_FRAMEWORK is set, model_<name|version|framework|path|code_dir/gitInfo]> must set")

		elif model_params['model_framework_type'] == "PRESET_MODEL":
			if model_params.get('model_name') and model_params.get('model_framework_type')  and model_params.get('model_version') \
							and model_params.get('model_framework') and model_params.get('model_path'):
				_config['name'] = model_params['model_name']
				_config['type'] = model_params['model_framework_type']
				_config['version'] = model_params['model_version']
				_config['presetModelId'] = model_params['model_framework']
				_config['modelPath'] = model_params['model_path']
				result = self.get_preset_model()
				result = json.loads(result.data.decode('utf-8'))
				preset_model_list = [ item['id'] for item in result['presetModels']]
				if _config['presetModelId'] not in preset_model_list:
					raise ValueError("model_framwork is not exist, please check it!")
			else:
				raise ValueError("when model_framework_type = PRESET_MODEL is set, model_<name|version|framework|path> must set")


		elif model_params['model_framework_type'] == "CUSTOM":
			if model_params.get('model_name') and model_params.get('model_framework_type')  and model_params.get('model_version') \
							and model_params.get('model_mirrorUrl'):

				_config['name'] = model_params['model_name']
				_config['type'] = model_params['model_framework_type']
				_config['version'] = model_params['model_version']
				if 'model_path' in model_params:
					_config['modelPath'] = model_params['model_path']
				_config['mirrorUrl'] = model_params['model_mirrorUrl']
			else:
				raise ValueError("when model_framework_type = CUSTOM is set, model_<name|version|mirrorUrl|path> must set")

		self.create_model_body = _config
		LOGGER.debug("=============Model:%s==================="%(_config['type']))
		LOGGER.debug(_config)

	def _generate_service_params(self, service_params):
		_config = {}
		if service_params['service_models'][0]['instanceCount'] is None:
			raise ValueError("instanceCount must set!")
		elif isinstance(service_params['service_models'][0]['instanceCount'],int) == False:
			raise ValueError("instanceCount must type of int!")
		elif service_params['service_models'][0]['instanceCount'] > 10:
			raise ValueError("instanceCount must < 10!")

		_config['name'] = service_params['service_name']
		_config['type'] = service_params['service_type']
		_config['serviceModels'] = service_params['service_models']

		result = self.get_predict_instance_types()
		result = json.loads(result.data.decode('utf-8'))
		resourceId_list = [ item['id'] for item in result['resources']]
		if _config['serviceModels'][0]['resourceId'] not in resourceId_list:
			raise ValueError("service_models['resourceId'] is not exist, please check it!")
		self.deploy_service_body = _config
		LOGGER.debug("=============Delopy===================")
		LOGGER.debug(_config)
	

#	@abstractmethod
#	def create_modelarts_model(self):
#		""" Creating model
#			Args:
#				session: Building interactions with Wangsu Cloud service.
#			Returns:
#				The model id that created successfully, will be used in deploying service.
#		"""
#		pass
#

#	@abstractmethod
#	def deploy_modelarts_predictor(self):
#		""" Deploying model predictor
#			Args:
#				session: Build interactions with Wangsu Cloud Service.
#			Returns:
#				Predictor.
#		"""
#		pass
#
#	@abstractmethod
#	def delete_model_endpoint(self):
#		""" Deleting model endpoint, including model and service.
#			It will print the deleting result.
#			Args:
#				 session: Building interactions with Wangsu Cloud Service.
#				 model(dict): including model id
#				 servide(dict): including service id
#		"""
#		pass
#
	def is_reach_maximum_times(self, max_attempt_times):
		if max_attempt_times > MAXIMUM_RETRY_TIMES:
			return True
		else:
			return False

#	@abstractmethod
#	def get_model_list(self):
#		"""
#		return User model list
#		"""
#		pass
#
#	@abstractmethod
#	def get_model_info(self):
#		"""
#		:return model information.
#		"""
#		pass
#
#
#	@abstractmethod
#	def get_model_version_info(self):
#		"""
#		:return model information.
#		"""
#		pass
#
#	@abstractmethod
#	def _get_service_list(self):
#		"""
#		return User service list
#		"""
#		pass
#
#	@abstractmethod
#	def _get_service_info(self):
#		"""
#		return: the service information
#		"""
#		pass
#
#	@abstractmethod
#	def delete_model_version(self):
#		"""
#		return: delete model endpoint
#		"""
#		pass
#
#
#	@abstractmethod
#	def delete_model(self):
#		"""
#		return: delete model endpoint
#		"""
#		pass
#
#	@abstractmethod
#	def delete_service(self):
#		"""
#		return: delete service endpoint
#		"""
#		pass

class ModelApiAccountImpl(ModelApiBase):
	""" A ModelMaker Model that can be created model, deployed model service and delete model endpoint. """

	def __init__(self, session):

		"""
		Initialize a ModelMaker Model instance.
		"""
		self.session = session
		self.model_api = ModelApi(self.session.client)
		self.service_api = ServiceApi(self.session.client)
		self.framework_api = FrameworkApi(self.session.client)
		self.spec_api = SpecApi(self.session.client)
		self.model_id	= None
		self.model_version_id = None
		self.service_id = None

	def create_modelmaker_model_version(self,model_id):
		""" Creating model
			Args:
				session: Building interactions with Wangsu Cloud service.
			Returns:
				The model id that created successfully, will be used in deploying service.
		"""
		self.model_id = model_id
		model_create_resp = self.model_api.create_the_version_model(project_id=self.session.project_id,
																body=self.create_model_body, model_id=self.model_id)
		data = json.loads(model_create_resp.data.decode('utf-8'))
		LOGGER.info("=============%s====================="%('Model Response'))
		LOGGER.info(data)
		self.model_version_id = data['versionId']

	def create_modelmaker_model(self, model_name):
		""" Creating model
			Args:
				session: Building interactions with Wangsu Cloud service.
			Returns:
				The model id that created successfully, will be used in deploying service.
		"""
		model_create_resp = self.model_api.create_the_model(project_id=self.session.project_id,
															body=self.create_model_body)
		data = json.loads(model_create_resp.data.decode('utf-8'))
		if data.get('errorCode'):
			if data['errorCode'] == 101009:
				result = self.get_model_info()
				result = json.loads(result.data.decode('utf-8'))
				for item in result['models']:
					if item['name'] == model_name:
						self.model_id = item['id']
						model_create_resp = self.model_api.create_the_version_model(project_id=self.session.project_id,
																	body=self.create_model_body, model_id=self.model_id)
						data = json.loads(model_create_resp.data.decode('utf-8'))
						LOGGER.info("=============%s==================="%('Model Response'))
						LOGGER.info(data)
						if data.get('errorCode'):
							raise Exception("create model  error!")
						else:
							self.model_version_id = data['versionId']
							return model_create_resp
				raise Exception("create model  error!")
			else:
				raise Exception("create model  error!")
		LOGGER.info("=============%s==================="%('Model Response'))
		LOGGER.info(data)
		self.model_id = data['id']
		self.model_version_id = data['versionId']
		return model_create_resp

	def deploy_modelmaker_predictor(self):
		""" Deploying model service
			Args:
				session: Build interactions with Wangsu Cloud Service.
			Returns:
				Predictor.
		"""
		service_deploy_resp = self.service_api.create_service(project_id=self.session.project_id,
															  body=self.deploy_service_body)
		#data = json.loads(service_deploy_resp.data.decode('utf-8'))
		data = str(service_deploy_resp.data, encoding="utf-8")
		data = eval(data)
		LOGGER.info("=============%s==================="%('Service Response'))
		LOGGER.info(data)
		if data.get('errorCode'):
				raise Exception("create service  error!")
		self.service_id = data['id']
	
#		count_status_query_times = 0
#		while True:
#			service_query_resp = self._get_service_info()
#			data = json.loads(service_query_resp.data.decode('utf-8'))
#			if data.get('errorCode'):
#				raise Exception("get service  info error!")
#
#			if super(ModelApiAccountImpl, self).is_reach_maximum_times(count_status_query_times):
#				print(
#					"Reach the maximum service status query times, the current status is %s" % data['status'])
#				break
#
#			if data['status'] == 'RUNNING':
#				print("\nDeploy finished")
#				break
#			elif data['status'] == 'DEPLOYING':
#				if count_status_query_times == 0:
#					print("\nDeploying...")
#				count_status_query_times += 1
#				time.sleep(MODEL_WAIT_SECOND)
#			elif data['status'] == 'DEPLOYING_FAIL':
#				print("\nDeploying failed")
#				break
#			elif data['status'] == 'STOPPING':
#				print("\nStopping")
#			elif data['status'] == 'STOPPED':
#				print("\nStopped")
#				break
#			else:
#				time.sleep(MODEL_WAIT_SECOND)
#		
		return PredictorApiAccountImpl(self.session, self.service_id)

#	def delete_model_endpoint(self, model_id=None, service_id=None):
#		""" Deleting model endpoint, including model and service.
#			It will print the deleting result.
#			Args:
#				 session: Building interactions with Wangsu Cloud Service.
#				 model(dict): including model id
#				 servide(dict): including service id
#		"""
#		if service_id is not None:
#			self.delete_service(service_id=service_id)
#			count_service_retry_times = 0
#			while True:
#				count_service_retry_times += 1
#				if super(ModelApiAccountImpl, self).is_reach_maximum_times(count_service_retry_times):
#					print("Can't get the service %s delete information." % service_id)
#					break
#
#				services_list = self._get_service_list()
#				if service_id in [tmp.service_id for tmp in services_list.services]:
#					time.sleep(MODEL_WAIT_SECOND)
#				else:
#					print('Delete the service %s endpoint successfully.' % service_id)
#					break
#
#		if model_id is not None:
#			self.delete_model(model_id=model_id)
#			count_model_retry_times = 0
#			while True:
#				count_model_retry_times += 1
#				if super(ModelApiAccountImpl, self).is_reach_maximum_times(count_model_retry_times):
#					print("Can't get the model %s delete information." % model_id)
#					break
#
#				model_list = self.get_model_list()
#				if model_id in [tmp.model_id for tmp in model_list.models]:
#					time.sleep(MODEL_WAIT_SECOND)
#				else:
#					print('Delete the model %s endpoint successfully.' % model_id)
#					break

	def get_predict_instance_types(self):
		""" get_preset_model
		"""

		body={}
		return self.spec_api.list_spec(project_id=self.session.project_id,body=body,env="PREDICT")

	def get_predict_framework_list(self):
		""" get_preset_model
		"""

		body={}
		return self.framework_api.get_framework_id(project_id=self.session.project_id, body=body, env="PREDICT")

	def get_preset_model(self):
		""" get_preset_model
		"""

		body={}
		return self.model_api.get_preset_model(project_id=self.session.project_id, body=body)

	def delete_model(self, model_id = None):
		""" Only delete model endpoint
		"""
		if model_id is None:
			raise ValueError('model_id is need!!!')

		body={}
		return self.model_api.delete_model(project_id=self.session.project_id, body=body, model_id=model_id)

	def delete_model_version(self, model_version_id = None):
		""" Only delete model endpoint
		"""
		if model_version_id is None and self.model_version_id:
			model_version_id = self.model_version_id
		elif model_version_id and self.model_version_id and model_version_id != self.model_version_id:
			print("Current model_version_id is %s, but it will replace by model_version_id %s"%(str(self.model_version_id),str(model_version_id)))
		elif model_version_id is None and self.model_version_id is None:
			raise ValueError("model_version_id is need, please create model first or model_version_id=xxx")
		body = {}

		return self.model_api.delete_model_version(project_id=self.session.project_id, body=body, model_version_id=model_version_id)


	def delete_service(self, service_id = None):
		""" Only delete model endpoint
		"""
		if service_id is None and self.service_id:
			service_id = self.service_id
		elif service_id and self.service_id and service_id != self.service_id:
			print("Current model_version_id is %s, but it will replace by model_version_id %s"%(str(self.service_id),str(service_id)))
		elif service_id is None and self.service_id is None:
			raise ValueError("service_id is need, please create deploy_predictor first or service_id=xxx")


		body={}
		return self.service_api.delete_micro_service(project_id=self.session.project_id, body=body, service_id=service_id)


	def get_model_info(self, model_id=None):
		"""
		:return model information.
		"""
#		if model_id is None:
#			raise ValueError('model_id is need!!!')

		body={}
		return self.model_api.get_model_info(project_id=self.session.project_id, model_id=model_id, body=body)


	def get_model_version_info(self, model_version_id=None):
		"""
		:return model information.
		"""
		if model_version_id is None and self.model_version_id:
			model_version_id = self.model_version_id
		elif model_version_id and self.model_version_id and model_version_id != self.model_version_id:
			print("Current model_version_id is %s, but it will replace by model_version_id %s"%(str(self.model_version_id),str(model_version_id)))
		elif model_version_id is None and self.model_version_id is None:
			raise ValueError("model_version_id is need, please create model first or model_version_id=xxx")

		body={}
		return self.model_api.get_model_version_info(project_id=self.session.project_id, model_version_id=model_version_id, body=body)

	def get_model_version_status(self, model_version_id=None):
		"""
		:return model information.
		"""
		if model_version_id is None:
			if hasattr(self,'model_version_id'):
				model_version_id = self.model_version_id
			else:
				raise ValueError('please use create_model method first or version_id is need!!!')
	
		body={}
		return self.model_api.get_model_version_info(project_id=self.session.project_id, model_version_id=model_version_id, body=body)


#	def _get_service_list(self):
#		"""
#		return User service list
#		"""
#		return self.service_api.get_service_list(project_id=self.session.project_id)
#
	def _get_service_info(self):
		"""
		return: the service information
		"""
		body={}
		return self.service_api.get_service_info(project_id=self.session.project_id, body=body, service_id=self.service_id)

