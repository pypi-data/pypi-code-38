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
class ModifyApiNameRequest(RoaRequest):

	def __init__(self):
		RoaRequest.__init__(self, 'Acs', '2015-01-01', 'ModifyApiName')
		self.set_uri_pattern('/modifyApiName')
		self.set_method('POST|GET')

	def get_ModifyName(self):
		return self.get_query_params().get('ModifyName')

	def set_ModifyName(self,ModifyName):
		self.add_query_param('ModifyName',ModifyName)

	def get_Name(self):
		return self.get_query_params().get('Name')

	def set_Name(self,Name):
		self.add_query_param('Name',Name)

	def get_ProductName(self):
		return self.get_query_params().get('ProductName')

	def set_ProductName(self,ProductName):
		self.add_query_param('ProductName',ProductName)

	def get_ChangeId(self):
		return self.get_query_params().get('ChangeId')

	def set_ChangeId(self,ChangeId):
		self.add_query_param('ChangeId',ChangeId)

	def get_VersionName(self):
		return self.get_query_params().get('VersionName')

	def set_VersionName(self,VersionName):
		self.add_query_param('VersionName',VersionName)