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
class StopPurchasedApiRequest(RoaRequest):

	def __init__(self):
		RoaRequest.__init__(self, 'Acs', '2015-01-01', 'StopPurchasedApi')
		self.set_uri_pattern('/Api/StopPurchasedApi')
		self.set_method('POST|GET')

	def get_PurchaseProduct(self):
		return self.get_query_params().get('PurchaseProduct')

	def set_PurchaseProduct(self,PurchaseProduct):
		self.add_query_param('PurchaseProduct',PurchaseProduct)

	def get_Channel(self):
		return self.get_query_params().get('Channel')

	def set_Channel(self,Channel):
		self.add_query_param('Channel',Channel)

	def get_PurchaseVersion(self):
		return self.get_query_params().get('PurchaseVersion')

	def set_PurchaseVersion(self,PurchaseVersion):
		self.add_query_param('PurchaseVersion',PurchaseVersion)

	def get_PurchaseApiName(self):
		return self.get_query_params().get('PurchaseApiName')

	def set_PurchaseApiName(self,PurchaseApiName):
		self.add_query_param('PurchaseApiName',PurchaseApiName)