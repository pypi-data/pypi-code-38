from __future__ import print_function
from .client.api import *
from .model import *
from datetime import datetime, timedelta
import time
#====================
import json
import logging
import pdb
#python 2 and python 3 compatibility library
from six import with_metaclass
from abc import ABCMeta, abstractmethod

logging.basicConfig()
LOGGER = logging.getLogger('modelmaker-sdk/Estimator')
LOGGER_LEVEL = os.getenv("MODELMAKER_LEVEL", logging.INFO) #cloud
LOGGER.setLevel(int(LOGGER_LEVEL))
ISOTIMEFORMAT = '%m%d-%H%M%S'
class EstimatorBase(with_metaclass(ABCMeta, object)):

	def __init__(self, modelmaker_session, train_instance_count=None, train_instance_type=None, volume_size=None,
				 output_path=None, max_runtime=None,**kwargs):

		self.modelmaker_session = modelmaker_session
		self.train_instance_count = train_instance_count
		self.train_instance_type = train_instance_type
		self.volume_size = volume_size
		self.max_runtime = max_runtime
		self.output_path = output_path
		self.job_name = None
		self.access_key = modelmaker_session.access_key
		self.secret_key = modelmaker_session.secret_key
		self.client = modelmaker_session.client
#		 self.project_id = modelmaker_session.project_id
		self.model_api = Model(modelmaker_session)
		self.log_id = 0

	def _prepare_for_training(self, job_name=None):
		if job_name is not None:
			self.job_name = job_name
		else:
			 raise ValueError('job name is needed for training')
		return self.job_name

	def fit(self, inputs=None, wait=False, logs=False, job_name=None):
		"""Train a model using the input training dataset.
		"""
		starttime = datetime.now()
		job_name = self._prepare_for_training(job_name=job_name)

#		if inputs is None:
#			raise ValueError('Input data is needed for training')
		data = _TrainingJob.start_new(self, inputs)
		version_id = data['versionId']
		self.job_id = data['id']
		self.version_id = version_id

		count_init = 0
		count_down_data = 0
		count_running = 0
		if wait:
			while True:
				result = self.get_job_version_status(self.modelmaker_session, version_id=version_id)
				if result.get('errorCode'):
				 	raise Exception("get train job info error!")
				status = result['status']
				if status == 'FINISH':
					endtime = datetime.now()
					duration = (endtime-starttime).seconds
					LOGGER.info("Job [ %s ] duration is %s seconds" % (job_name, duration))
					LOGGER.info("=============%s==================="%('Output'))
					output = self._get_job_output(version_id=version_id)
					LOGGER.info(output)
					break
				elif status == 'STARTING_FAIL':
					endtime = datetime.now()
					duration = (endtime-starttime).seconds
					LOGGER.info("Job [ %s ] duration is %s seconds" % (job_name, duration))
					LOGGER.info("Job [ %s ] is %s" % (job_name, "start failed"))
					time.sleep(3)
					break
				elif status == 'TRAINING_FAIL':
					endtime = datetime.now()
					duration = (endtime-starttime).seconds
					LOGGER.info("Job [ %s ] duration is %s seconds" % (job_name, duration))
					LOGGER.info("Job [ %s ] is %s" % (job_name, "train failed"))
					time.sleep(3)
					break
				elif status == 'STARTING':
					if count_init == 0:
						LOGGER.info(status)
						LOGGER.info("Job [ %s ] is %s" % (job_name, "starting..."))
					count_init = count_init + 1
					#LOGGER.info("Job [ %s ] is %s" % (job_name, "starting"))
					time.sleep(3)
				elif status == 'STOPPING':
					LOGGER.info("Job [ %s ] is %s" % (job_name, "stoping..."))
					time.sleep(3)
				elif status == 'DOWNLOAD_DATA':
					if count_down_data == 0:
						LOGGER.info(status)
						LOGGER.info("Job [ %s ] is %s" % (job_name, "download data..."))
					time.sleep(3)
					count_down_data = count_down_data + 1
				elif status == 'TRAINING':
					if count_running == 0:
						print("")
						LOGGER.info(status)
					count_running = count_running + 1
					if logs == True:
						log_result = self._get_job_log(version_id=version_id, log_id=self.log_id)
						if log_result.get('logs'):
							log_msg = log_result['logs']
							if len(log_msg):
								for item in log_msg:
									LOGGER.info(item['content'])
								self.log_id = int(log_msg[-1]['id']) + 1
							else:
								pass
								#self.log_id = log_result['logs'][0]['id']
								#LOGGER.info("log is Null")
							#self.log_id = log_result['logs'][0]['id']
						else:
							pass
							#LOGGER.info("log is Null")
					time.sleep(8)
				else:
					LOGGER.info("Job [ %s ] status is %s, please check log" % (job_name, status))
					break

		return data

	def print_job_middle_state(self, state, count_init):
		count_init = count_init - 1
		print(state + '|' + '>>>>>>' * count_init+'|',end='\r')

	@classmethod
	def preset_model(cls, modelmaker_session):
		result = _TrainingJob.get_preset_model(modelmaker_session)
		LOGGER.info(result)
		return result

	@classmethod
	def preset_algorithm(cls, modelmaker_session):
		result = _TrainingJob.get_preset_algorithm(modelmaker_session)
		LOGGER.info(result)
		return result

	@classmethod
	def train_framework(cls, modelmaker_session):
		result = _TrainingJob.get_framework_list(modelmaker_session,'TRAIN')
		LOGGER.info(result)
		return result

	@classmethod
	def development_framework(cls, modelmaker_session):
		result = _TrainingJob.get_framework_list(modelmaker_session,'DEVELOPMENT')
		LOGGER.info(result)
		return result

	@classmethod
	def predict_framework(cls, modelmaker_session):
		result = _TrainingJob.get_framework_list(modelmaker_session,'PREDICT')
		LOGGER.info(result)
		return result

	@classmethod
	def train_machine(cls, modelmaker_session):
		result = _TrainingJob.get_instance_types(modelmaker_session,'TRAIN')
		LOGGER.info(result)
		return result

	@classmethod
	def development_machine(cls, modelmaker_session):
		result = _TrainingJob.get_instance_types(modelmaker_session,'DEVELOPMENT')
		LOGGER.info(result)
		return result

	@classmethod
	def predict_machine(cls, modelmaker_session):
		result = _TrainingJob.get_instance_types(modelmaker_session,'PREDICT')
		LOGGER.info(result)
		return result

	@classmethod
	def get_spec_list(cls, modelmaker_session, env):
		return _TrainingJob.get_spec_list(modelmaker_session,env)

	@classmethod
	def version_info(cls, modelmaker_session, version_id):
		result =  _TrainingJob.get_job_version_info(modelmaker_session, version_id)
		LOGGER.info(result)
		return result
	
	@classmethod
	def get_job_version_status(cls, modelmaker_session, version_id):
		return  _TrainingJob.get_job_version_info(modelmaker_session, version_id)

	@classmethod
	def Info(cls, modelmaker_session, job_id=None):
		result = _TrainingJob.get_job_info(modelmaker_session, job_id=job_id)
		LOGGER.info(result)
		return result

	def info(self, version_id=None):
		if version_id is None:
			if hasattr(self,'version_id'):
				version_id = self.version_id
			else:
				LOGGER.error("please use fit() method first or version_id is need!!!")
				return
		modelmaker_session = self.modelmaker_session
		result =  _TrainingJob.get_job_version_info(modelmaker_session, version_id)
		LOGGER.info(result)
		return result

	def stop(self, version_id=None):
		if version_id is None:
				if hasattr(self,'version_id'):
					version_id = self.version_id
				else:
					LOGGER.error("please use fit() method first or version_id is need!!!")
					return
		modelmaker_session = self.modelmaker_session
		result = _TrainingJob.stop_job(modelmaker_session, version_id)
		LOGGER.info(result)
		return result

	def delete(self, version_id=None):
		if version_id is None:
				if hasattr(self,'version_id'):
					version_id = self.version_id
				else:
					LOGGER.error("please use fit() method first or version_id is need!!!")
					return
		modelmaker_session = self.modelmaker_session
		result = _TrainingJob.delete_job_version(modelmaker_session, version_id)
		LOGGER.info(result)
		return result

	@classmethod
	def destory_job_version(cls, modelmaker_session, version_id=None):
		if version_id is None:
				LOGGER.error("version_id is need")
		result = _TrainingJob.delete_job_version(modelmaker_session, version_id)
		LOGGER.info(result)
		return result

	@classmethod
	def destory_job(cls, modelmaker_session, job_id=None):
		if job_id is None:
				LOGGER.error("job_id is need")
				return
		result = _TrainingJob.delete_job(modelmaker_session, job_id)
		LOGGER.info(result)
		return result

	def _get_job_log(self, version_id, log_id):
		result =  _TrainingJob.get_job_log(self, version_id, log_id)
		return result

	def log(self, log_id,version_id=None):
		if version_id is None:
			if hasattr(self,'version_id'):
				version_id = self.version_id
			else:
				LOGGER.error("please use fit() method first or version_id is need!!!")
				return

		result =  _TrainingJob.get_job_log(self, version_id, log_id)
		LOGGER.info(result)
		return result

	def _get_job_output(self, version_id):
		result =  _TrainingJob.get_job_output(self, version_id)
		return result

	def artifacts(self, version_id=None):
		if version_id is None:
			if hasattr(self,'version_id'):
				version_id = self.version_id
			else:
				LOGGER.error("please use fit() method first or version_id is need!!!")
				return

		result =  _TrainingJob.get_job_output(self, version_id)
		LOGGER.info(result)
		return result

	def resource(self, version_id=None):
		if version_id is None:
			if hasattr(self,'version_id'):
				version_id = self.version_id
			else:
				LOGGER.error("please use fit() method first or version_id is need!!!")
				return
		result =  _TrainingJob.get_resource_monitor(self, version_id)
		LOGGER.info("============")
		LOGGER.info(result)
		return result

	def metric(self, version_id=None):
		if version_id is None:
			if hasattr(self,'version_id'):
				version_id = self.version_id
			else:
				LOGGER.error("please use fit() method first or version_id is need!!!")
				return
		result =  _TrainingJob.get_performance_monitor(self, version_id)
		LOGGER.info(result)
		return result

	def create_model(self, version_id=None, **kwargs):
		""" creating model interface
		:param kwargs: Create model body params
		:return: model instance
		"""
		if version_id is None:
			if hasattr(self,'version_id'):
				version_id = self.version_id
			else:
				LOGGER.error("please use fit() method first or version_id is need!!!")
				return

		result = self.get_job_version_status(self.modelmaker_session, version_id=version_id)
		if result.get('errorCode'):
			raise Exception("get train job info error!")
		status = result['status']
		if status == 'FINISH':
			if kwargs.get('model_path') == None:
				if self.output_path == None:
					raise ValueError('model_path is None!')
				else:
					kwargs['model_path'] = self.output_path
			if kwargs.get('model_name') == None:
				if self.job_name == None:
					raise ValueError('model_name is None!')
				else:
					kwargs['model_name'] = self.job_name

			if kwargs.get('model_framework_type') == None:
				if self.framework_type == None:
					raise ValueError('model_framework_type is None!')
				else:
					if self.framework_type == "PRESET_ALGORITHM":
						kwargs['model_framework_type'] = "PRESET_MODEL"
						if kwargs.get('model_framework') == None:
							if self.algorithm == None:
								raise ValueError('model_framework is None!')
							else:
								result = _TrainingJob.get_preset_algorithm(self.modelmaker_session)
								presetAlgorithms_id_name_dict = { item['id']:item['name'] for item in result['presetAlgorithms']}
								preset_model_name = presetAlgorithms_id_name_dict[self.algorithm]
								result = _TrainingJob.get_preset_model(self.modelmaker_session)
								preset_model_name_id_dict = { item['name']:item['id'] for item in result['presetModels']}
								try:
									kwargs['model_framework'] = preset_model_name_id_dict[preset_model_name]
								except Exception as e:
									raise Exception("model_framework must set!", e)
					elif self.framework_type == "BASIC_FRAMEWORK":
						kwargs['model_framework_type'] = self.framework_type
						if kwargs.get('model_framework') == None:
							if self.framework == None:
								raise ValueError('model_framework is None!')
							else:
								result = _TrainingJob.get_framework_list(self.modelmaker_session,'TRAIN')
								basic_framework_id_name_dict = { item['id']:item['name'] for item in result['frameWorks']}
								basic_model_name = basic_framework_id_name_dict[self.framework]
								result = _TrainingJob.get_framework_list(self.modelmaker_session,'PREDICT')
								basic_framework_name_id_dict = { item['name']:item['id'] for item in result['frameWorks']}
								try:
									kwargs['model_framework'] = basic_framework_name_id_dict[basic_model_name]
								except Exception as e:
									raise Exception("model_framework must set!", e)
						kwargs['model_code_dir'] = _TrainingJob.s3_user_code_upload(self.modelmaker_session,kwargs['model_code_dir'])
					else:
						kwargs['model_framework_type'] = self.framework_type
			create_model_resp = self.model_api.create_model(**kwargs)
			return self.model_api
		else:
			raise Exception("train job is not finish!")

	def deploy_predictor(self, **kwargs):
		"""Deploying model service interface
		:param kwargs:  Deploying predictor body params
		:return:  predictor
		"""
#		if kwargs.get('service_name') == None and self.model_name is None:
#			ISOTIMEFORMAT = '%m%d-%H%M%S'
#			beijing_date = (datetime.now()+ timedelta(hours=8)).strftime(ISOTIMEFORMAT)
#			kwargs['service_name'] = self.job_name + '-' + beijing_date
		if kwargs.get('service_type') == None:
			kwargs['service_type'] = "ONLINE_SERVICE"
		deploy_model_resp = self.model_api.deploy_predictor(**kwargs)
		return deploy_model_resp

class _TrainingJob():

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

	@classmethod
	def s3_check_parameter(cls,path):
		if path is None:
			pass
		elif isinstance(path,str):
			if path.startswith("s3://") == True:
				pass
			else:
				raise ValueError('%s must conform to "s3://XXX"'%path)
		elif isinstance(path,list):
			for item in path:
				if item is None: 
					pass
				elif item.startswith("s3://") == True:
					pass
				else:
					raise ValueError('%s must conform to "s3://XXX"'%item)
		else:
			raise ValueError('Type must str or list')

	@classmethod
	def prepare_config(cls, estimator, inputs):
		Framework = ["TensorFlow-1.13.1-python3.5","MXNET-python3.5","Caffe-python3.5"]
		Framework_type = ["BASIC_FRAMEWORK","PRESET_ALGORITHM","CUSTOM"]
		_config = {}
		_config['name'] = estimator.job_name
		_config['type'] = estimator.framework_type
		## environment check
		if estimator.train_instance_count is None:
			raise ValueError("train_instance_count must set!")
		elif isinstance(estimator.train_instance_count,int) == False:
			raise ValueError("train_instance_count must type of int!")
		elif estimator.train_instance_count > 10:
			raise ValueError("train_instance_count < 10!")
		
		if estimator.volume_size is None:
			raise ValueError("volume_size must set!")
		elif isinstance(estimator.volume_size,int) == False:
			raise ValueError("volume_size must type of int!")
		elif estimator.volume_size > 10:
			raise ValueError("volume_size < 10!")
		if estimator.train_instance_type is None:
			raise ValueError("train_instance_type must set!")
	
		_config['resourceId'] = estimator.train_instance_type
		_config['volumeSize'] = estimator.volume_size
		_config['instance'] = estimator.train_instance_count
		_config['maxRuntime'] = estimator.max_runtime
		## framwork check
		if estimator.framework_type == None or estimator.framework_type not in Framework_type:
			 raise ValueError('framework_type is must setted in "BASIC_FRAMEWORK","PRESET_ALGORITHM","CUSTOM" ')
		else:
			if estimator.framework_type == "BASIC_FRAMEWORK":
				## framwork parameter check
				if estimator.boot_file and estimator.framework and estimator.output_path and inputs and (estimator.code_dir or estimator.gitInfo):
					_config['codeUrl'] = estimator.code_dir
					_config['gitInfo'] = estimator.git_info
					_config['frameworkId'] = estimator.framework
					_config['startup'] = estimator.boot_file
					_config['parameters'] = estimator.hyperparameters
					_config['inputFiles'] = estimator.input_files
					_config['dataUrl'] = inputs
					_config['output'] = estimator.output_path
					_config['monitors'] = estimator.monitors
					_TrainingJob.s3_check_parameter([_config['dataUrl'],_config['output']])
					if _config['frameworkId'] is None:
						raise ValueError("when framework_type=BASIC_FRAMEWORK , framework must set")
					else:
						result = _TrainingJob.get_framework_list(estimator.modelmaker_session,'TRAIN')
						frameworkId_list = [ item['id'] for item in result['frameWorks']]
						if _config['frameworkId'] not in frameworkId_list:
							raise ValueError("framework is not exist, please check it!")
						_config['codeUrl'] = _TrainingJob.s3_user_code_upload(estimator.modelmaker_session,_config['codeUrl'])
				else:
			 		raise ValueError('When framework_type is "BASIC_FRAMEWORK",<boot_file|framework|output_path|inputs|[code_dir/git_info]> is need')
			elif estimator.framework_type == "PRESET_ALGORITHM":
				## framwork parameter check
				if estimator.algorithm and estimator.output_path and inputs:
					_config['algorithmId'] = estimator.algorithm
					_config['parameters'] = estimator.hyperparameters
					_config['modeUrl'] = estimator.init_model
					_config['dataUrl'] = inputs
					_config['output'] = estimator.output_path
					_TrainingJob.s3_check_parameter([_config['dataUrl'],_config['output']])
					if _config['algorithmId'] is None:
						raise ValueError("when framework_type=PRESET_ALGORITHM , algorithm must set")
					else:
						result = _TrainingJob.get_preset_algorithm(estimator.modelmaker_session)
						algorithmId_list = [ item['id'] for item in result['presetAlgorithms']]
						if _config['algorithmId'] not in algorithmId_list:
							raise ValueError("algorithmId is not exist, please check it!")
				else:
			 		raise ValueError('When framework_type is "PRESET_ALGORITHM",<algorithm|inputs|output_path> is need')
			elif estimator.framework_type == "CUSTOM":
				## framwork parameter check
				if estimator.user_image_url and estimator.output_path:
					_config['gitInfo'] = estimator.git_info
					_config['mirrorUrl'] = estimator.user_image_url
					_config['codeUrl'] = estimator.code_dir
					_config['envs'] = estimator.env
					_config['command'] = estimator.user_command
					_config['args'] = estimator.user_command_args
					_config['dataUrl'] = inputs
					_config['output'] = estimator.output_path
					_config['monitors'] = estimator.monitors
					#pdb.set_trace()
					_TrainingJob.s3_check_parameter([_config['dataUrl'],_config['output']])
					_config['codeUrl'] = _TrainingJob.s3_user_code_upload(estimator.modelmaker_session,_config['codeUrl'])
				else:
			 		raise ValueError('When framework_type is "CUSTOM",<user_image_url|inputs|output_path> is need')

			result = _TrainingJob.get_instance_types(estimator.modelmaker_session,'TRAIN')
			resourceId_list = [ item['id'] for item in result['resources']]
			if _config['resourceId'] not in resourceId_list:
				raise ValueError("train_instance_type is not exist, please check it!")

		return _config

	@classmethod
	def start_new(cls, estimator, inputs):
		"""Create a new training job from the estimator.
		"""
		project_id = estimator.modelmaker_session.project_id
		client = estimator.modelmaker_session.client

		if estimator.job_description is None:
			estimator.job_description = ""

		_config = _TrainingJob.prepare_config(estimator, inputs)

		body = _config
		#pdb.set_trace()
		LOGGER.debug("=============Train:%s==================="%(_config['type']))
		LOGGER.debug(body)
		if estimator.modelmaker_session.auth == 'token':
			train_job_api = TrainJobApi(client)
			res = train_job_api.create_training_job(project_id=project_id, body=body)
			data = json.loads(res.data.decode('utf-8'))
			if data.get('errorCode'):
				if data['errorCode'] == 102009:
					result = _TrainingJob.get_job_info(estimator.modelmaker_session,job_id=None)
					for item in result['trainTasks']:
						if item['name'] == estimator.job_name:
							job_id = item['id']
							res = train_job_api.create_training_job_version(project_id=project_id, job_id=job_id, body=body)
							data = json.loads(res.data.decode('utf-8'))
							if data.get('errorCode'):
								LOGGER.info(data)
								raise Exception("create train job error!")
							LOGGER.info("=============%s==================="%('Response'))
							LOGGER.info(data)
							return data
				else:
					LOGGER.info(data)
					raise Exception("create train job error!")
			LOGGER.info("=============%s==================="%('Response'))
			LOGGER.info(data)
			return data
		else:
			data = 0
			return data

	@classmethod
	def get_preset_model(cls, modelmaker_session):
		project_id = modelmaker_session.project_id
		client = modelmaker_session.client
		body={}
		if modelmaker_session.auth == 'token':
			model_api = ModelApi(client)
			res = model_api.get_preset_model(project_id=project_id, body=body)
			data = json.loads(res.data.decode('utf-8'))
		else:
			data = 1
		return data

	@classmethod
	def get_preset_algorithm(cls, modelmaker_session):
		project_id = modelmaker_session.project_id
		client = modelmaker_session.client
		body={}
		if modelmaker_session.auth == 'token':
			algorithm_api = AlgorithmApi(client)
			res = algorithm_api.get_preset_algorithm(project_id=project_id, body=body)
			data = json.loads(res.data.decode('utf-8'))
		else:
			data = 1
		return data

	@classmethod
	def get_framework_list(cls, modelmaker_session, env):
		project_id = modelmaker_session.project_id
		client = modelmaker_session.client
		body={}
		if modelmaker_session.auth == 'token':
			framework_api = FrameworkApi(client)
			res = framework_api.get_framework_id(project_id=project_id, body=body, env=env)
			data = json.loads(res.data.decode('utf-8'))
		else:
			data = 1
		return data

	@classmethod
	def get_instance_types(cls, modelmaker_session, env):
		res = cls.get_spec_list(modelmaker_session, env)
		data = json.loads(res.data.decode('utf-8'))
		return data

	@classmethod
	def get_spec_list(cls, modelmaker_session, env):
		project_id = modelmaker_session.project_id
		client = modelmaker_session.client
		body={}
		if modelmaker_session.auth == 'token':
			spec_api = SpecApi(modelmaker_session.client)
			res = spec_api.list_spec(project_id=project_id,body=body,env=env)
		else:
			rest = 1
		return res

	#/*get job info, a job haver multi version*/#
	@classmethod
	def get_job_info(cls, modelmaker_session, job_id):
		project_id = modelmaker_session.project_id
		client = modelmaker_session.client

		body={}
		if modelmaker_session.auth == 'token':
			train_job_api = TrainJobApi(modelmaker_session.client)
			res = train_job_api.training_job_info(project_id=project_id, job_id=job_id, body=body)
			job_info = json.loads(res.data.decode('utf-8'))
		else:
			job_info = 1
		return job_info

	#/*get job version info*#
	@classmethod
	def get_job_version_info(cls, modelmaker_session, version_id):
		project_id = modelmaker_session.project_id
		client = modelmaker_session.client

		body={}
		if modelmaker_session.auth == 'token':
			train_job_api = TrainJobApi(modelmaker_session.client)
			res = train_job_api.training_job_version_status(project_id=project_id, version_id=version_id, body=body)
			data = json.loads(res.data.decode('utf-8'))
		else:
			data = 1
		return data

	@classmethod
	def get_job_log(cls, estimator, version_id, log_id):
		project_id = estimator.modelmaker_session.project_id
		client = estimator.modelmaker_session.client

		body={}
		if estimator.modelmaker_session.auth == 'token':
			train_job_api = TrainJobApi(estimator.modelmaker_session.client)
			res = train_job_api.training_job_log(project_id=project_id, version_id=version_id, log_id=log_id, body=body)
			data = json.loads(res.data.decode('utf-8'))
		else:
			data = 1
		return data

	@classmethod
	def get_resource_monitor(cls, estimator, version_id):
		project_id = estimator.modelmaker_session.project_id
		client = estimator.modelmaker_session.client

		body={}
		if estimator.modelmaker_session.auth == 'token':
			train_job_api = TrainJobApi(estimator.modelmaker_session.client)
			res = train_job_api.training_resource_monitor(project_id=project_id, version_id=version_id, body=body)
			data = json.loads(res.data.decode('utf-8'))
		else:
			data = 1
		return data

	@classmethod
	def get_performance_monitor(cls, estimator, version_id):
		project_id = estimator.modelmaker_session.project_id
		client = estimator.modelmaker_session.client

		body={}
		if estimator.modelmaker_session.auth == 'token':
			train_job_api = TrainJobApi(estimator.modelmaker_session.client)
			res = train_job_api.training_performance_monitor(project_id=project_id, version_id=version_id, body=body)
			data = json.loads(res.data.decode('utf-8'))
		else:
			data = 1
		return data

	@classmethod
	def get_job_output(cls, estimator, version_id):
		project_id = estimator.modelmaker_session.project_id
		client = estimator.modelmaker_session.client

		body={}
		if estimator.modelmaker_session.auth == 'token':
			train_job_api = TrainJobApi(estimator.modelmaker_session.client)
			res = train_job_api.training_job_output(project_id=project_id, version_id=version_id, body=body)
			data = json.loads(res.data.decode('utf-8'))
		else:
			data = 1
		return data

	@classmethod
	def stop_job(cls, modelmaker_session, version_id):
		project_id = modelmaker_session.project_id
		client = modelmaker_session.client

		body={}
		if modelmaker_session.auth == 'token':
			train_job_api = TrainJobApi(modelmaker_session.client)
			res = train_job_api.stop_job(project_id=project_id, version_id=version_id, body=body)
			data = json.loads(res.data.decode('utf-8'))
		else:
			data = 1
		return data

	@classmethod
	def delete_job(cls, modelmaker_session, job_id):
		project_id = modelmaker_session.project_id
		client = modelmaker_session.client

		body={}
		if modelmaker_session.auth == 'token':
			train_job_api = TrainJobApi(modelmaker_session.client)
			res = train_job_api.delete_job(project_id=project_id, job_id=job_id, body=body)
			data = json.loads(res.data.decode('utf-8'))
		else:
			data = 1
		return data

	@classmethod
	def delete_job_version(cls, modelmaker_session, version_id):
		project_id = modelmaker_session.project_id
		client = modelmaker_session.client

		body={}
		if modelmaker_session.auth == 'token':
			train_job_api = TrainJobApi(modelmaker_session.client)
			res = train_job_api.delete_job_version(project_id=project_id, version_id=version_id, body=body)
			data = json.loads(res.data.decode('utf-8'))
		else:
			data = 1
		return data


class Estimator(EstimatorBase):

	def __init__(self, code_dir=None, boot_file=None, hyperparameters=None, framework = None, framework_type=None, algorithm=None, 
				 input_files=None, model_name=None, init_model=None, env=None, user_image_url=None, user_command=None, user_command_args=None,
				 monitors=None, job_description=None, git_info=None, **kwargs):

		self.code_dir = code_dir
		self.boot_file = boot_file
		self.hyperparameters = hyperparameters or []
		self.framework = framework
		self.framework_type = framework_type
		self.algorithm = algorithm
		self.input_files = input_files
		self.model_name = model_name
		self.init_model = init_model
		self.env = env
		self.user_image_url = user_image_url
		self.user_command = user_command
		self.user_command_args = user_command_args
		self.monitors = monitors
		self.git_info = git_info
		self.job_description = job_description

		super(Estimator, self).__init__(**kwargs)

