# coding: utf-8

"""
	ModelMaker SDK
"""


from __future__ import absolute_import


# python 2 and python 3 compatibility library
#import six

from modelmaker.client.api_client import ApiClient


class TrainJobApi(object):

	def __init__(self, api_client=None):
		if api_client is None:
			api_client = ApiClient()
		self.api_client = api_client

	def create_training_job(self, project_id, body, **kwargs):
		kwargs['_return_http_data_only'] = True
		(data) = self.create_training_job_with_http_info(project_id, body, **kwargs)
		return data

	def create_training_job_with_http_info(self, project_id, body, **kwargs):

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(
			['application/json'])

		# Authentication setting
		auth_settings = ['ApiTokenAuth']
		return self.api_client.call_api(
			'/v1/train', 'POST',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def create_training_job_version(self, project_id, job_id, body, **kwargs):
		kwargs['_return_http_data_only'] = True
		(data) = self.create_training_job_version_with_http_info(project_id, job_id, body, **kwargs)
		return data

	def create_training_job_version_with_http_info(self, project_id, job_id, body, **kwargs):

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(
			['application/json'])

		# Authentication setting
		auth_settings = ['ApiTokenAuth']
		return self.api_client.call_api(
			'/v1/train/%s/version'%(str(job_id)), 'POST',
			header_params,
			body=body,
			auth_settings=auth_settings)
	
	def training_job_info(self, project_id, job_id, body, **kwargs):
		kwargs['_return_http_data_only'] = True
		(data) = self.training_job_info_with_http_info(project_id, job_id, body, **kwargs)
		return data

	def training_job_info_with_http_info(self, project_id, job_id, body, **kwargs):

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(
			['application/json'])

		# Authentication setting
		auth_settings = ['ApiTokenAuth']
		if job_id == None:
				domain='/v1/train'
		else:
				domain='/v1/train/' + str(job_id)
		return self.api_client.call_api(
			domain, 'GET',
			header_params,
			body=body,
			auth_settings=auth_settings)


	def training_job_version_status(self, project_id, version_id, body, **kwargs):
		kwargs['_return_http_data_only'] = True
		(data) = self.training_job_version_status_with_http_info(project_id, version_id, body, **kwargs)
		return data

	def training_job_version_status_with_http_info(self, project_id, version_id, body, **kwargs):

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(
			['application/json'])

		# Authentication setting
		auth_settings = ['ApiTokenAuth']
		return self.api_client.call_api(
			'/v1/train/version/'+str(version_id), 'GET',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def training_job_log(self, project_id, version_id, body, log_id, **kwargs):
		kwargs['_return_http_data_only'] = True
		(data) = self.training_job_log_with_http_info(project_id, version_id, body, log_id, **kwargs)
		return data

	def training_job_log_with_http_info(self, project_id, version_id, body, log_id, **kwargs):

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(
			['application/json'])

		# Authentication setting
		auth_settings = ['ApiTokenAuth']
		return self.api_client.call_api(
			'/v1/train/version/%s/log?lastId=%s'%(str(version_id),str(log_id)), 'GET',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def training_resource_monitor(self, project_id, version_id, body, **kwargs):
		kwargs['_return_http_data_only'] = True
		(data) = self.training_resource_monitor_with_http_info(project_id, version_id, body, **kwargs)
		return data

	def training_resource_monitor_with_http_info(self, project_id, version_id, body, **kwargs):

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])  

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(  
			['application/json'])  

		# Authentication setting
		auth_settings = ['ApiTokenAuth']  
		return self.api_client.call_api(
			'/v1/train/version/%s/resource-monitor'%(str(version_id)), 'GET',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def training_performance_monitor(self, project_id, version_id, body, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.training_performance_monitor_with_http_info(project_id, version_id, body, **kwargs)  
		return data

	def training_performance_monitor_with_http_info(self, project_id, version_id, body, **kwargs):  

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])  

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(  
			['application/json'])  

		# Authentication setting
		auth_settings = ['ApiTokenAuth']  
		return self.api_client.call_api(
			'/v1/train/version/%s/performance-monitor'%(str(version_id)), 'GET',
			header_params,
			body=body,
			auth_settings=auth_settings)
	def stop_job(self, project_id, version_id, body, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.stop_job_version_with_http_info(project_id, version_id, body, **kwargs)  
		return data

	def stop_job_version_with_http_info(self, project_id, version_id, body, **kwargs):  

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])  

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(  
			['application/json'])  

		# Authentication setting
		auth_settings = ['ApiTokenAuth']  
		return self.api_client.call_api(
			'/v1/train/%s/stop'%str(version_id), 'POST',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def delete_job_version(self, project_id, version_id, body, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.delete_job_version_with_http_info(project_id, version_id, body, **kwargs)  
		return data

	def delete_job_version_with_http_info(self, project_id, version_id, body, **kwargs):  

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])  

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(  
			['application/json'])  

		# Authentication setting
		auth_settings = ['ApiTokenAuth']  
		return self.api_client.call_api(
			'/v1/train/version/'+str(version_id), 'DELETE',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def delete_job(self, project_id, job_id, body, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.delete_job_with_http_info(project_id, job_id, body, **kwargs)  
		return data

	def delete_job_with_http_info(self, project_id, job_id, body, **kwargs):  

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])  

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(  
			['application/json'])  

		# Authentication setting
		auth_settings = ['ApiTokenAuth']  
		return self.api_client.call_api(
			'/v1/train/'+str(job_id), 'DELETE',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def training_job_output(self, project_id, version_id, body, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.training_job_output_with_http_info(project_id, version_id, body, **kwargs)  
		return data

	def training_job_output_with_http_info(self, project_id, version_id, body, **kwargs):  

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])  

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(  
			['application/json'])  

		# Authentication setting
		auth_settings = ['ApiTokenAuth']  
		return self.api_client.call_api(
			'/v1/train/version/%s/output'%(str(version_id)), 'GET',
			header_params,
			body=body,
			auth_settings=auth_settings)


