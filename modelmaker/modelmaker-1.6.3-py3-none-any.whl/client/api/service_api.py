# coding: utf-8

"""
	ModelMaker SDK
"""


from __future__ import absolute_import

# python 2 and python 3 compatibility library
import six

from modelmaker.client.api_client import ApiClient


class ServiceApi(object):
	def __init__(self, api_client=None):
		if api_client is None:
			api_client = ApiClient()
		self.api_client = api_client

	def create_service(self, project_id, body, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.create_service_with_http_info(project_id, body, **kwargs)  
		return data

	def create_service_with_http_info(self, project_id, body, **kwargs):  

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
			'/v1/service', 'POST',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def get_service_info(self, project_id, body, service_id, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.get_service_info_with_http_info(project_id, body, service_id, **kwargs)  
		return data

	def get_service_info_with_http_info(self, project_id, body, service_id, **kwargs):  

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])  

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(  
			['application/json'])  

		# Authentication setting
		auth_settings = ['ApiTokenAuth']  
		if service_id == None:
			domain="/v1/service"
		else:
			domain="/v1/service/"+str(service_id)
		return self.api_client.call_api(
			domain, 'GET',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def operate_a_service(self, project_id, body, service_id, action_body, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.operate_a_service_info_with_http_info(project_id, body, service_id, action_body, **kwargs)  
		return data

	def operate_a_service_info_with_http_info(self, project_id, body, service_id, action_body, **kwargs):  

		header_params = {}
		# HTTP header `Accept`
		header_params['Accept'] = self.api_client.select_header_accept(
			['application/json'])  

		# HTTP header `Content-Type`
		header_params['Content-Type'] = self.api_client.select_header_content_type(  
			['application/json'])  

		# Authentication setting
		auth_settings = ['ApiTokenAuth']  
		domain="/v1/service/%s/%s"%(str(service_id),str(action_body))
		#print(domain)
		return self.api_client.call_api(
			domain, 'POST',
			header_params,
			body=body,
			auth_settings=auth_settings)

	def delete_micro_service(self, project_id, body, service_id, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.delete_service_info_with_http_info(project_id, body, service_id, **kwargs)  
		return data

	def delete_service_info_with_http_info(self, project_id, body, service_id, **kwargs):  

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
			"/v1/service/"+str(service_id), 'DELETE',
			header_params,
			body=body,
			auth_settings=auth_settings)

