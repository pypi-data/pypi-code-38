# OMF.py
#
# Copyright (C) 2018-2019 OSIsoft, LLC. All rights reserved.
#
# THIS SOFTWARE CONTAINS CONFIDENTIAL INFORMATION AND TRADE SECRETS OF
# OSIsoft, LLC.  USE, DISCLOSURE, OR REPRODUCTION IS PROHIBITED WITHOUT
# THE PRIOR EXPRESS WRITTEN PERMISSION OF OSIsoft, LLC.
#
# RESTRICTED RIGHTS LEGEND
# Use, duplication, or disclosure by the Government is subject to restrictions
# as set forth in subparagraph (c)(1)(ii) of the Rights in Technical Data and
# Computer Software clause at DFARS 252.227.7013
#
# OSIsoft, LLC
# 1600 Alvarado St, San Leandro, CA 94577


from urllib.parse import urlparse
import urllib.request, urllib.parse, urllib.error
import http.client as http
import json

from .SdsError import SdsError
from .SDS.SdsStream import SdsStream
from .SDS.SdsType import SdsType
from .SDS.SdsStreamView import SdsStreamView
from .SDS.SdsStreamViewMap import SdsStreamViewMap
from .SDS.SdsBoundaryType import SdsBoundaryType
import requests


class OMF(object):
    def __init__(self, apiversion, tenant, url, producerToken, omfNamespace):
        self.__apiVersion = apiversion
        self.__tenant = tenant
        self.__baseURL = url
        self.__producerToken = producerToken
        self.__omfNamespace = omfNamespace

        self.__omfEndpoint = self.__baseURL + '/api/' +  self.__apiVersion + '/tenants/' + self.__tenant + '/namespaces/' + self.__omfNamespace +'/omf'


