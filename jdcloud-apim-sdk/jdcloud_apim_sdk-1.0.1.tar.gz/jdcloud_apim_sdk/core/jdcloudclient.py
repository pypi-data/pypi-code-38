# coding=utf8

# Copyright 2018 JDCLOUD.COM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import traceback
import requests
from jdcloud_apim_sdk.core import const
from jdcloud_apim_sdk.core.signer import Signer
from jdcloud_apim_sdk.core.version import VERSION
from jdcloud_apim_sdk.core.parameterbuilder import WithBodyBuilder, WithoutBodyBuilder
from jdcloud_apim_sdk.core.exception import ClientException
from jdcloud_apim_sdk.core.logger import get_default_logger, INFO, ERROR
from jdcloud_apim_sdk.core.util import base64encode


class JDCloudClient(object):

    def __init__(self, credential, config, service_name, revision, logger):
        self.__config = config
        self.__service_name = service_name
        self.__credential = credential
        self.__revision = revision
        self.__logger = logger

        if logger is None:
            self.__logger = get_default_logger()

        self.__builder_map = {const.METHOD_GET: WithoutBodyBuilder,
                              const.METHOD_DELETE: WithoutBodyBuilder,
                              const.METHOD_HEAD: WithoutBodyBuilder,
                              const.METHOD_PUT: WithBodyBuilder,
                              const.METHOD_POST: WithBodyBuilder,
                              const.METHOD_PATCH: WithBodyBuilder}

    def send(self, request):
        if self.__config is None:
            raise ClientException('Miss config object')
        if request is None:
            raise ClientException('Miss request object')

        region = self.__get_region_id(request)

        try:
            header = self.__merge_headers(request.header)
            if hasattr(request, 'file') and request.file:
                header[const.JDCLOUD_CONTENT_SHA256] = const.JDCLOUD_CONTENT_SHA256_VALUE
            token = header.get(const.JDCLOUD_SECURITY_TOKEN, '')

            param_builder = self.__builder_map[request.method]()
            url = param_builder.build_url(request, self.__config.scheme, self.__config.endpoint)
            body = param_builder.build_body(request)
            self.__logger.log(INFO, 'url=' + url)

            if self.__credential is not None and self.__credential.access_key and self.__credential.secret_key:
                signer = Signer(self.__logger)
                signer.sign(method=request.method, region=region, uri=url,
                            headers=header, data=body, credential=self.__credential,
                            security_token=token, service=self.__service_name)
            self.__logger.log(INFO, header)

            resp = requests.request(request.method, url, data=body, headers=header,
                                    timeout=self.__config.timeout)
            self.__logger.log(INFO, resp.content)

            return resp
        except Exception as expt:
            msg = traceback.format_exc()
            self.__logger.log(ERROR, msg)
            raise expt

    def __merge_headers(self, request_header):
        headers = dict()
        headers['User-Agent'] = 'JdcloudSdkPython/%s %s/%s' % (VERSION, self.__service_name, self.__revision)
        headers['Content-Type'] = 'application/json'

        if request_header is not None and isinstance(request_header, dict):
            for key, value in request_header.items():
                if key.lower() in const.HEADER_ERROR:
                    raise ClientException('Please use header with prefix x-jdcloud')
                if key.lower() in const.HEADER_BASE64:
                    value = base64encode(value)
                headers[key] = value

        self.__logger.log(INFO, headers)
        return headers

    def __get_region_id(self, request):
        if not request.parameters or not hasattr(request.parameters, 'regionId') or request.parameters.regionId is None:
            return 'jdcloud-api'  # when no region, use this value to fill field for sign
        return request.parameters.regionId
