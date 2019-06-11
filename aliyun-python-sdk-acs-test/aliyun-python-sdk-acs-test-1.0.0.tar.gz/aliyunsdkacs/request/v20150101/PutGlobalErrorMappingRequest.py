# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from aliyunsdkcore.request import RoaRequest
class PutGlobalErrorMappingRequest(RoaRequest):

	def __init__(self):
		RoaRequest.__init__(self, 'Acs', '2015-01-01', 'PutGlobalErrorMapping')
		self.set_uri_pattern('/ErrorMapping')
		self.set_method('PUT')

	def get_ContentLength(self):
		return self.get_headers().get('Content-Length')

	def set_ContentLength(self,ContentLength):
		self.add_header('Content-Length',ContentLength)

	def get_BodyContent(self):
		return self.get_body_params().get('BodyContent')

	def set_BodyContent(self,BodyContent):
		self.add_body_params('BodyContent', BodyContent)

	def get_ContentMD5(self):
		return self.get_headers().get('Content-MD5')

	def set_ContentMD5(self,ContentMD5):
		self.add_header('Content-MD5',ContentMD5)

	def get_ContentType(self):
		return self.get_headers().get('Content-Type')

	def set_ContentType(self,ContentType):
		self.add_header('Content-Type',ContentType)

	def get_Accept(self):
		return self.get_headers().get('Accept')

	def set_Accept(self,Accept):
		self.add_header('Accept',Accept)