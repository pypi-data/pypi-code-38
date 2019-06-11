# coding: utf-8

"""
	ModelMaker SDK
"""


from __future__ import absolute_import


# python 2 and python 3 compatibility library
import six

from modelmaker.client.api_client import ApiClient


class ModelApi(object):
	def __init__(self, api_client=None):
		if api_client is None:
			api_client = ApiClient()
		self.api_client = api_client

	def create_the_model(self, project_id, body, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.create_model_with_http_info(project_id, body, **kwargs)  
		return data

	def create_model_with_http_info(self, project_id, body, **kwargs):  

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
			'/v1/model', 'POST',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def create_the_version_model(self, project_id, body, model_id, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.create_version_model_with_http_info(project_id, body, model_id, **kwargs)  
		return data

	def create_version_model_with_http_info(self, project_id, body, model_id, **kwargs):  

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
			'/v1/model/%s/version/'%(str(model_id)), 'POST',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def get_model_info(self, project_id, body, model_id, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.get_model_info_with_http_info(project_id, body, model_id, **kwargs)  
		return data

	def get_model_info_with_http_info(self, project_id, body, model_id, **kwargs):  

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])  

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(  
			['application/json'])  

		# Authentication setting
		auth_settings = ['ApiTokenAuth']  
		if model_id == None:
			domain="/v1/model"
		else:
			domain="/v1/model/"+str(model_id)
		return self.api_client.call_api(
			domain, 'GET',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def get_model_version_info(self, project_id, body, model_version_id, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.get_model_version_info_with_http_info(project_id, body, model_version_id, **kwargs)  
		return data

	def get_model_version_info_with_http_info(self, project_id, body, model_version_id, **kwargs):  

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
			'/v1/model/version/'+str(model_version_id), 'GET',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def get_preset_model(self, project_id, body, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.get_preset_model_with_http_info(project_id, body, **kwargs)  
		return data

	def get_preset_model_with_http_info(self, project_id, body, **kwargs):  

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
			'/v1/preset-model', 'GET',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def delete_model(self, project_id, body, model_id, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.delete_model_info_with_http_info(project_id, body, model_id, **kwargs)  
		return data

	def delete_model_info_with_http_info(self, project_id, body, model_id, **kwargs):  

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])  

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(  
			['application/json'])  

		# Authentication setting
		auth_settings = ['ApiTokenAuth']  
		print("/v1/model/"+str(model_id))
		return self.api_client.call_api(
			"/v1/model/"+str(model_id), 'DELETE',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def delete_model_version(self, project_id, body, model_version_id, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.delete_model_version_info_with_http_info(project_id, body, model_version_id, **kwargs)  
		return data

	def delete_model_version_info_with_http_info(self, project_id, body, model_version_id, **kwargs):  

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
			"/v1/model/version/"+str(model_version_id), 'DELETE',
			header_params,
			body=body,
			auth_settings=auth_settings)
