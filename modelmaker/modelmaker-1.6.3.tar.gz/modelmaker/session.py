#-*-coding:utf-8-*-
import os
import logging
import json
import hashlib
import re
from .config.auth import authorize_by_token 
from .config.auth import get_temporary_aksk_without_commission
from .config.config import create_client
from .util.s3_util import WCS
import pdb
logging.basicConfig()
LOGGER = logging.getLogger('modelmaker-sdk/session')
MODELMAKER_CONFIG = os.getenv("MODELMAKER_CONFIG", "~/.modelmaker/config.json") #cloud
LOGGER_LEVEL = os.getenv("MODELMAKER_LEVEL", logging.INFO) #cloud
LOGGER.setLevel(int(LOGGER_LEVEL))
#MODELMAKER_CONFIG = os.getenv("MODELMAKER_CONFIG", "~/.modelmaker/config2.json")  #31.5


class Session(object):
	"""Manage interactions with the Wangsu services needed.

	This class provides convenient methods for manipulating other services,
	such as iam auth, operation in WSS3.

	"""
	def __init__(self, config_file=None, username=None, password=None, host_base=None, project_id=None, region=None, bucket=None):
		"""Initialize a SageMaker ``Session``.

		Args:
			username : Wangsu cloud ai username.
			password : Wangsu cloud ai password.
			host_base : Wangsu cloud api server domain.
			region : Wangsu cloud api server domain.
		"""
		ip_pattern = r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}"
		if config_file:
			self.config_file = config_file
		else:
			self.config_file = os.path.expanduser(MODELMAKER_CONFIG)
		#-----------------bucket-----------------	
		self.bucket=None
		if bucket:
			if bucket.endswith('/') == False:
				self.bucket=bucket+"/"
		else:
			if os.path.exists(self.config_file):
				with open(self.config_file) as f:
					config_json = json.load(f)
					if config_json.get('iam_config') and config_json['iam_config'].get('bucket'):
						self.bucket = config_json['iam_config']['bucket']
						if self.bucket.endswith('/') == False:
							self.bucket=self.bucket+"/"
					else:
						LOGGER.warning("The bucket is not set!!!")
			else:
				LOGGER.warning("The bucket is not set!!!")

		#-----------------username password-----------------	
		if username and password:
			self.username = username
			self.password = password
		elif username == None and password == None:
			if os.path.exists(self.config_file):
				with open(self.config_file) as f:
					config_json = json.load(f)
					if config_json.get('iam_config') and config_json['iam_config'].get('username') and config_json['iam_config'].get('password'):
						self.username = config_json['iam_config']['username']
						self.password = config_json['iam_config']['password']
					else:
						raise ValueError("username/password must be set in session(username=xxx,password=xxx) or in config file")
			else:
				raise ValueError("username/password must be set in session(username=xxx,password=xxx) or in config file")
		else:
			raise ValueError("username/password must be set in session(username=xxx,password=xxx) or in config file")

		self.s3_protocol = "http"
		self.verify_ssl = True
		self.region = "js01"
		self.host_base = "https://mmr.wangsucloud.com:9948/mmr"
		self.iam_server = None
		#-----------------host_base-----------------	
		if host_base:
			if host_base.startswith("https://") == False and host_base.startswith("http://") == False:
				raise ValueError('host_base must start with http:// or https://')
			else:
				self.host_base = host_base
		else:
			if os.path.exists(self.config_file):
				with open(self.config_file) as f:
					config_json = json.load(f)
					if config_json.get('iam_config') and config_json['iam_config'].get('host_base'):
						self.host_base = config_json['iam_config']['host_base']
						if self.host_base.startswith("http://") == False and self.host_base.startswith("https://") == False:
							raise ValueError('%s [host_base] must start with http:// or https://'%(self.config_file))
					else:
						LOGGER.warning("host_base set default:%s"%self.host_base)
			else:
				LOGGER.warning("host_base set default:%s"%self.host_base)
		
		#-----------------region-----------------	
		if region:
			self.region = region
		else:
			if os.path.exists(self.config_file):
				with open(self.config_file) as f:
					config_json = json.load(f)
					if config_json.get('iam_config') and config_json['iam_config'].get('region'):
						self.region = config_json['iam_config']['region']
					else:
						LOGGER.warning("region set default:%s"%self.region)
			else:
				LOGGER.warning("region set default:%s"%self.region)
		
		if self.host_base and self.region:
			pattern  = re.compile(ip_pattern)
			m = pattern.findall(self.host_base)
			if m:
				self.iam_server = self.host_base
			else:
				split_domain = self.host_base.split("://")
				self.iam_server = "{procol}://{region}{domain}".format(procol=split_domain[0],region=self.region,domain=split_domain[1])

		#-----------------verify_ssl,s3_protocol-----------------	
		if os.path.exists(self.config_file):
			with open(self.config_file) as f:
				config_json = json.load(f)
				if config_json.get('iam_config') and config_json['iam_config'].get('verify_ssl') != None:
					self.verify_ssl = config_json['iam_config']['verify_ssl']
				else:
					LOGGER.warning("verify_ssl set default:%s"%self.verify_ssl)
				if config_json.get('iam_config') and config_json['iam_config'].get('s3_protocol'):
					self.s3_protocol = config_json['iam_config']['s3_protocol']
				else:
					LOGGER.warning("s3_protocol set default:%s"%self.s3_protocol)
					
		if LOGGER_LEVEL == 10:
			LOGGER.debug({'username':self.username, 'password':self.password, 'iam_server':self.iam_server, 'bucket':self.bucket})
		else:
			LOGGER.info({'username':self.username, 'password':self.password.replace(self.password,'*'*len(self.password)), 'iam_server':self.iam_server, 'bucket':self.bucket})

		#pdb.set_trace()
		if self.username and self.password and self.iam_server:
				try:
					token = authorize_by_token(username=self.username,
															password=self.password,
															endpoint=self.iam_server,
															verify_ssl=self.verify_ssl)
				except Exception as e:
						raise Exception("Get token failed! ", e)
				LOGGER.debug({'response':{'token':token}})
				self.token = token
				try:
					res = get_temporary_aksk_without_commission(token, self.iam_server,verify_ssl=self.verify_ssl)
				except Exception as e:
						raise Exception("Get ak/sk failed! ", e)
				self.access_key, self.secret_key, self.s3_endpoint_url, self.s3_region, self.s3_mirror_auth, self.s3_mirror_endpoint_url = res
				if LOGGER_LEVEL == 10:
					LOGGER.debug({'response':{'url':self.s3_endpoint_url,'ak':self.access_key,'sk':self.secret_key,'region':self.s3_region}})
				else:
					LOGGER.info({'response':{'url':self.s3_endpoint_url,'ak':self.access_key,'sk':self.secret_key.replace(self.secret_key,'*'*len(self.secret_key)),'region':self.s3_region}})
				self.s3_client = WCS(endpoint_url=self.s3_endpoint_url, ak=self.access_key, sk=self.secret_key, region=self.s3_region, method=self.s3_protocol)
				self.client = create_client(context="default", access_key=self.access_key, secret_key=self.secret_key, \
									username=self.username, password=self.password, host=self.iam_server, verify_ssl=self.verify_ssl, token=self.token)
				self.auth = "token"
		else:
			raise Exception('username and password and iam_server is need!')
		if project_id:
			self.project_id = project_id
		elif "PROJECT_ID" in os.environ:
			self.project_id = os.environ["PROJECT_ID"]
		else:
			self.project_id = 0
			#LOGGER.warning("The project_id is set to default 0")
		LOGGER.info("Init Success")

	def upload_data(self, bucket_path, path):
		"""Upload local file or directory to s3.
		"""
		bucket, key = self.s3_client.check_bucket_path(bucket_path)
		if isinstance(path, list):
			self.s3_client.put_multi_objects(bucket=bucket, key=key, bucket_path=bucket_path, local_file_paths=path)
		elif isinstance(path, str):
			if not os.path.exists(path):
				raise Exception("Path " + path + " does not exist!")
			if os.path.isdir(path):
				self.s3_client.put_directory(bucket=bucket, key=key, bucket_path=bucket_path, local_directory=path)
			elif os.path.isfile(path):
				self.s3_client.put_object(bucket=bucket, key=key, bucket_path=bucket_path, local_file_path=path)
		else:
			raise Exception('local path should be list or string')

	#仅支持path是路径
	def download_data(self, bucket_path, path):
		if os.path.isdir(path) == False:
			raise Exception("Path must folder!")
		if not os.path.exists(path):
			raise Exception("Path " + path + " does not exist!")
		is_directory = bucket_path.endswith('/')
		#bucket_path = self.s3_client.check_bucket_path(bucket_path)
		if is_directory:
			#bucket_path = ai-team/edfg/, path='./download'
			bucket, key = self.s3_client.check_bucket_path(bucket_path)
			self.s3_client.download_directory(bucket=bucket, key=key, bucket_path=bucket_path, local_storage_path=path)
		else:
			#bucket_path = ai-team/edfg/a.txt, path='./download'
			self.s3_client.download_object(bucket_path=bucket_path, local_file_path=path)

	#仅支持一层层创建,bucket_path以'/'结尾
	def create_directory(self, bucket_path, directory):
		bucket, key = self.s3_client.check_bucket_path(bucket_path)
		self.s3_client.create_directory(bucket, key, directory)
	#删除再创建依旧存在,bucket_path以'/'结尾
	def delete_directory(self, bucket_path, directory):
		bucket, key = self.s3_client.check_bucket_path(bucket_path)
		self.s3_client.delete_directory(bucket, key, directory)
