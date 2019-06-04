# coding=utf-8
from __future__ import print_function

class Environments(object):

    def __init__(self, args):
        self._args = args

    def get_attributes(self):
        if self._args.env == 'ypprod':
            return self._getYPProdEnv()
        if self._args.env == 'ypqa':
            return self._getYPQAEnv()
        if self._args.env == 'ys1dev':
            return self._getYS1DevEnv()
        if self._args.env == 'icp':
            return self._getICPEnv()

    def _getYPProdEnv(self):
        attributes = {}
        attributes['name'] = 'YPPROD'
        attributes['api'] = 'https://api.ng.bluemix.net'
        attributes['aios_url'] = 'https://api.aiopenscale.cloud.ibm.com'
        attributes['iam_url'] = 'https://iam.bluemix.net/identity/token'
        attributes['uaa_url'] = 'https://login.ng.bluemix.net/UAALoginServerWAR/oauth/token'
        attributes['resource_controller_url'] = 'https://resource-controller.bluemix.net'
        attributes['resource_group_url'] = 'https://resource-manager.bluemix.net'
        return attributes

    def _getYPQAEnv(self):
        attributes = {}
        attributes['name'] = 'YPQA'
        attributes['api'] = 'https://api.ng.bluemix.net'
        attributes['aios_url'] = 'https://api.aiopenscale.test.cloud.ibm.com'
        attributes['iam_url'] = 'https://iam.bluemix.net/identity/token'
        attributes['uaa_url'] = 'https://login.ng.bluemix.net/UAALoginServerWAR/oauth/token'
        attributes['resource_controller_url'] = 'https://resource-controller.bluemix.net'
        attributes['resource_group_url'] = 'https://resource-manager.bluemix.net'
        return attributes

    def _getYS1DevEnv(self):
        attributes = {}
        attributes['name'] = 'YS1DEV'
        attributes['api'] = 'https://api.stage1.ng.bluemix.net'
        attributes['aios_url'] = 'https://aiopenscale-dev.us-south.containers.appdomain.cloud'
        attributes['iam_url'] = 'https://iam.stage1.bluemix.net/identity/token'
        attributes['uaa_url'] = 'https://login.stage1.ng.bluemix.net/UAALoginServerWAR/oauth/token'
        attributes['resource_controller_url'] = 'https://resource-controller.stage1.bluemix.net'
        attributes['resource_group_url'] = 'https://resource-manager.stage1.bluemix.net'
        return attributes

    def _getICPEnv(self):
        attributes = {}
        attributes['name'] = 'ICP'
        attributes['api'] = None
        attributes['aios_url'] = self._args.url
        attributes['iam_url'] = None
        attributes['uaa_url'] = None
        attributes['resource_controller_url'] = None
        attributes['resource_group_url'] = None
        return attributes
