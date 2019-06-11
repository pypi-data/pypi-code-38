import sys, os, datetime, hashlib, hmac
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import logging
from ..exception.iam_exception import IAMException
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.basicConfig()
LOGGER = logging.getLogger('modelmaker-sdk/auth')
LOGGER_LEVEL = os.getenv("MODELMAKER_LEVEL", logging.INFO) #cloud
LOGGER.setLevel(int(LOGGER_LEVEL))

def get_temporary_aksk_without_commission(token, iam_url, verify_ssl=True):
	"""get IAM's temporary AK/SK without commission which lasts for 24h
		:return: {
				 "s3": {
					 "ak": "111111",
					 "sk": "23423423",
					 }
				 "mirror": {
					 "auth":"23423423",
					 "url":"http:sdf"
				 }
				 }
	"""
	headers = {
		"Auth-Token": token,
		"Content-Type": "application/json"
	}
	if iam_url.startswith("https://") == False and iam_url.startswith("http://") == False:
		raise ValueError('iam_url must start with http:// or https://')
	host = iam_url
	url = host + "/v1/account/auth-access"
	LOGGER.debug("Get ak/sk>>>>>>>>>>>>>")
	LOGGER.debug("url:"+url)
	LOGGER.debug({'headers':headers})
	try:
		response = requests.get(url, headers=headers, verify=verify_ssl)
		if response.status_code > 300:
			raise IAMException(code=response.status_code, message="Connect iam server error!!!")
		else:
			access_key = response.json()['s3']['ak']
			secret_key = response.json()['s3']['sk']
			s3_endpoint_url = response.json()['s3']['url']
			s3_region = response.json()['s3']['region']
			s3_mirror_auth = response.json()['mirror']['auth']
			s3_mirror_endpoint_url = response.json()['mirror']['url']
			return access_key,secret_key,s3_endpoint_url,s3_region,s3_mirror_auth,s3_mirror_endpoint_url
	except IAMException:
		raise IAMException(code=response.status_code, message="Connect iam server error!!!")
	except Exception as e:
		raise Exception(e)

def authorize_by_token(username, password, endpoint, verify_ssl=True):
	"""
	Set auth information to client configure
	:param username:  User name
	:param password:  User password
	:return:
	"""
	if username is None or password is None:
		raise IllegalArgumentError("username and password can not be None")
	if endpoint is None:
		raise IllegalArgumentError("iam_server can not be None")
	body = {
			"username":username,
			"password":password
	}
	headers = {
		"Content-Type": "application/json"
	}
	if endpoint.startswith("https://") == False and endpoint.startswith("http://") == False:
		raise ValueError('iam_url must start with http:// or https://')
	host = endpoint
	url = host + "/v1/auth-token"
	LOGGER.debug("Get Token>>>>>>>>>>>>>")
	LOGGER.debug("url:"+url)
	LOGGER.debug({'headers':headers,'body':body})
	try:
		 response = requests.post(url, headers=headers, verify=verify_ssl, data=json.dumps(body))
		 if response.status_code > 300:
			 raise IAMException(code=response.status_code, message="Connect iam server error!!!")
		 else:
			 result = response.json()
			 token = response.json()['token']
			 #duration = response.json()['duration']
			 #return token, duration
			 return token
	except IAMException:
		 raise IAMException(code=response.status_code, message="Connect iam server error!!!")
	except Exception as e:
		 raise Exception(e)

