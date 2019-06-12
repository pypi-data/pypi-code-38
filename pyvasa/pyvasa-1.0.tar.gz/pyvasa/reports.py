#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author Hannes Ebelt <hannes.ebelt@sap.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

import requests
import os
from builtins import object
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
os.environ["CURL_CA_BUNDLE"] = ""


class Reports(object):
	def __init__(self, port=None, url=None, token=None, api_version='1.0'):
		self.api = api_version
		self.port = str(port)
		self.url = "https://" + url + ":" + self.port + "/api/rest/" + self.api + "/admin/report/"

		if token is not None:
			self.token = token

	def get_datastores_report(self):
		api_endpoint = "datastores"
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}

		r = requests.get(url=url_action, headers=headers, verify=False)

		try:
			datastore_details = r.json()
		except ValueError:
			datastore_details = dict()

		datastore_details['status_code'] = r.status_code

		return datastore_details

	def get_virtual_machines_report(self):
		api_endpoint = "virtual-machines"
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}

		r = requests.get(url=url_action, headers=headers, verify=False)

		try:
			vm_details = r.json()
		except ValueError:
			vm_details = dict()

		vm_details['status_code'] = r.status_code

		return vm_details
