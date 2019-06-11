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
class PutAccountBindingRequest(RoaRequest):

	def __init__(self):
		RoaRequest.__init__(self, 'Acs', '2015-01-01', 'PutAccountBinding')
		self.set_uri_pattern('/AccountBinding/[Product]/[AliyunUid]/[BucEmpId]')
		self.set_method('PUT')

	def get_Product(self):
		return self.get_path_params().get('Product')

	def set_Product(self,Product):
		self.add_path_param('Product',Product)

	def get_AliyunUid(self):
		return self.get_path_params().get('AliyunUid')

	def set_AliyunUid(self,AliyunUid):
		self.add_path_param('AliyunUid',AliyunUid)

	def get_BucEmpId(self):
		return self.get_path_params().get('BucEmpId')

	def set_BucEmpId(self,BucEmpId):
		self.add_path_param('BucEmpId',BucEmpId)

	def get_Accept(self):
		return self.get_headers().get('Accept')

	def set_Accept(self,Accept):
		self.add_header('Accept',Accept)