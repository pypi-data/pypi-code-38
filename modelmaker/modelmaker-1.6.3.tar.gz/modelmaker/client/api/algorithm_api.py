# coding: utf-8

"""
	ModelMaker SDK
"""


from __future__ import absolute_import

#import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from modelmaker.client.api_client import ApiClient

class AlgorithmApi(object):
	def __init__(self, api_client=None):
		if api_client is None:
			api_client = ApiClient()
		self.api_client = api_client

	def get_preset_algorithm(self, project_id, body, **kwargs):	
		kwargs['_return_http_data_only'] = True
		(data) = self.get_preset_algorithm_with_http_info(project_id, body, **kwargs)  
		return data

	def get_preset_algorithm_with_http_info(self, project_id, body, **kwargs):  

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
			'/v1/preset-algorithm', 'GET',
			header_params,
			body=body,
			auth_settings=auth_settings)

