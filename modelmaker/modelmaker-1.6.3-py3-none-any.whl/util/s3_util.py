from ..exception.s3_exception import S3Exception,S3UploadException,S3DownloadException
import sys
import boto3
from boto3.session import Session
import logging
import os
import shutil

logging.basicConfig()
LOGGER = logging.getLogger('s3')
LOGGER.setLevel(logging.DEBUG)

class WCS():
	"""
		WSS3 SDK Operation using temporary AK/SK
	"""
	def __init__(self, endpoint_url=None, ak=None, sk=None, region=None, security_token=None, is_secure=True, path_style=True,method="http"):
		"""AK SK and security_token comes from IAM's temporary AK/SK API
		"""
		if ak is None or sk is None or endpoint_url is None:
			raise Exception("Parameter is illegal!")

		self.endpoint_url = endpoint_url
		self.ak = ak
		self.sk = sk
		self.region = region
		self.session = Session(aws_access_key_id=self.ak,aws_secret_access_key=self.sk, region_name=self.region)
		if method == "http" and self.endpoint_url.startswith("http://") == False and self.endpoint_url.startswith("https://") == False:
			self.endpoint_url = "http://"+self.endpoint_url	
		if method == "https" and self.endpoint_url.startswith("https://") == False and self.endpoint_url.startswith("http://") == False:
			self.endpoint_url = "https://"+self.endpoint_url
		self.s3 = self.session.resource('s3', endpoint_url=self.endpoint_url)
		self.client = self.session.client('s3', endpoint_url=self.endpoint_url)

	def check_bucket_path(self, bucket_path):
		if bucket_path.startswith('/'):
			bucket_path = bucket_path[1:]
		if bucket_path.endswith('/') == False:
			raise ValueError("bucket_path is must end of '/'")
		bucket, key = bucket_path.split('/',1)

		return bucket, key

	def put_object( self, bucket, key, bucket_path, local_file_path):
		"""put local file to s3
			if the bucket_name does not exist in S3, then it will throw 404 exception
			if the bucket path does not exist in the bucket Name, then it will be created
			if S3 has existed the file in the specified path, then it will be overwritten
		"""
		try:
			if not os.path.exists(local_file_path):
				raise Exception("File " + local_file_path + " does not exist!")
			file_name = os.path.split(local_file_path)[-1]

			cloud_path = os.path.join(key,file_name)
			resp = self.client.put_object(Bucket=bucket, Key=cloud_path, Body=open(local_file_path, 'rb'))

			LOGGER.info("Successfully upload file %s to S3 %s" % (local_file_path, bucket_path))
#		except S3UploadException:
#			raise S3Exception(code=resp.errorCode, message=resp.errorMessage)
		except Exception as e:
			raise Exception("Upload file to S3 failed! ", e)

	def put_directory(self, bucket, key, bucket_path, local_directory):
		"""put multi local files to S3
			if the bucket_name does not exist in S3, then it will throw 404 exception
			if the bucket path does not exist in the bucket Name, then it will be created
			if S3 has existed the file in the specified path, then it will be overwritten
		"""
		print(bucket,key,bucket_path)
		if not os.path.exists(local_directory):
			raise Exception("Directory " + local_directory + " does not exist!")
		dir_name = os.path.split(local_directory)[-1] #获取顶级目录名
		dir_list=[]
		file_list=[]
		g_dir_file = os.walk(local_directory)
		for path, dirs, files in g_dir_file:
				tmp_path = path
				sub_dir = tmp_path.split(local_directory)
				create_dir_name = dir_name + sub_dir[1] #顶级目录名+子目录
				dir_list.append(create_dir_name)
				for file_name in files:
						file_list.append((create_dir_name,os.path.join(path, file_name)))
		print(dir_list)
		print(file_list)
		for item in dir_list:
			try:
				self.create_directory(bucket, key, item)
			except Exception as e:
				raise Exception("create_directory to S3 failed! ", e)
		for key_sub, directory in file_list:
			try:
				cloud_path = os.path.join(key, key_sub)
				self.put_object(bucket, cloud_path, os.path.join(bucket_path,key_sub), directory)
			except Exception as e:
				raise Exception("Upload file to S3 failed! ", e)

	def put_multi_objects(self, bucket, key, bucket_path, local_file_paths):
		"""put local directory to S3, splitted using ','
			if the bucket_name does not exist in S3, then it will throw 404 exception
			if the bucket path does not exist in the bucket Name, then it will be created
			if S3 has existed the file in the specified path, then it will be overwritten
		"""
		for local_file_path in local_file_paths:
			try:
				if not os.path.exists(local_file_path):
					raise Exception("File " + local_file_path + " does not exist!")
				if os.path.isdir(local_file_path):
					self.put_directory(bucket, key, bucket_path, local_file_path)
				else:
					self.put_object(bucket, key, bucket_path, local_file_path)
			except Exception as e:
				raise Exception("Upload multi files to S3 failed! ", e)

	def download_object(self, bucket_path, local_file_path):
		"""download S3 file to your local file
			if local path has existed the file, then it will be overwritten
		"""
		try:
			bucket_path_split = bucket_path.split('/',1)
			bucket_name = bucket_path_split[0]
			object_name = bucket_path_split[1]
			file_name = object_name.split('/')[-1]
			local_file_path = os.path.join(local_file_path, file_name)
			resp = self.client.download_file(Bucket=bucket_name, Key=object_name, Filename=local_file_path)
			LOGGER.info('download_file:'+ os.path.join(bucket_name, object_name) + ' to ' + local_file_path)
		except Exception as e:
			raise Exception("Download file from S3 failed! ", e)

	def mkdir_file(self,file_path):

		path, file_name  = os.path.split(file_path)
		folder = os.path.exists(path)
		if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
		    os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
#		file1 = open(file_path,'w')
#		file1.close()
#		return path

	def download_directory(self, bucket, key, bucket_path, local_storage_path):
		"""download S3 directory to your local path
			if local path has existed the file, then it will be overwritten
		"""
		dir_name = bucket_path.split('/')[-2]
		try:
			resp = self.client.list_objects(Bucket=bucket, Prefix=key)
			if resp.get('Contents'):
				for obj in resp['Contents']:
					#print(obj['Key'],key)
					#print(obj['Key'].split(key))
					#print(obj['Key'],key)
					combine_path = os.path.join(dir_name, obj['Key'].split(key)[1])
					local_file_path = os.path.join(local_storage_path, combine_path)
					self.mkdir_file(local_file_path)
					resp = self.client.download_file(Bucket=bucket, Key=obj['Key'], Filename=local_file_path)
					LOGGER.info('download_dir:'+ os.path.join(bucket, obj['Key']) + ' to ' + local_file_path)
			else:
				LOGGER.error('download_dir:'+ bucket_path+ " is NULL!")
		except Exception as e:
			raise Exception("Download directory from S3 failed! ", e)

	def create_directory(self, bucket, key, directory):
		"""
		Create a directory in bucket.
		"""

		if directory[-1] != "/":
			directory = directory + "/"
		
		if directory[0]  == "/":
			directory = directory[1:]
		cloud_directory = os.path.join(key, directory)
		try:
			create_dir_resp = self.client.put_object(Bucket=bucket, Key=cloud_directory)
		except Exception as e:
			raise Exception("create_dir directory to S3 failed! ", e)
		LOGGER.info('create_dir:'+ os.path.join(bucket,cloud_directory))

	def delete_directory(self, bucket, key, directory):
		"""
		Delete a directory in bucket.
		"""
		if directory[-1] != "/":
			directory = directory + "/"
		
		if directory[0]  == "/":
			directory = directory[1:]
		cloud_directory = os.path.join(key, directory)
		try:
			resp = self.client.list_objects(Bucket=bucket, Prefix=cloud_directory)
			if resp.get('Contents'):
				for obj in resp['Contents']:
					delete_dir_resp = self.client.delete_object(Bucket=bucket, Key=obj['Key'])
			else:
				delete_dir_resp = self.client.delete_object(Bucket=bucket, Key=cloud_directory)
		except Exception as e:
			raise Exception("delete_dir directory to S3 failed! ", e)
		LOGGER.info('delete_dir:'+ os.path.join(bucket,cloud_directory))


