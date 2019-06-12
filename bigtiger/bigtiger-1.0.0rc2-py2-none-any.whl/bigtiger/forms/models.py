# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

from __future__ import unicode_literals

from django.conf import settings


class WSDLModel(object):

    def __init__(self):
        pass

    def get_api_service_url(self, asmx_name):
        """获取webservice数据服务地址.
        """
        return '{}{}?wsdl'.format(settings.WEBSERVICE_ROOT_URL, asmx_name)

    def get_remote_api_service_url(self, asmx_name):
        """获取远程webservice数据服务地址.
        """
        return '{}{}?wsdl'.format(settings.REMOTE_WEBSERVICE_ROOT_URL, asmx_name)


class SQLAichemyModel(object):

    def __init__(self):
        pass
