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


class StorageCapabilityProfile(object):
	def __init__(self, port=None, url=None, vp_user=None, vp_password=None, token=None, api_version='1.0'):
		self.api = api_version
		self.port = str(port)
		self.url = "https://" + url + ":" + self.port + "/api/rest/" + self.api + "/admin/storage-capabilities"
		self.vp_user = vp_user
		self.vp_password = vp_password

		if token is not None:
			self.token = token

	def get_storage_capability_profiles(self):
		url_action = self.url
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}

		r = requests.get(url=url_action, headers=headers, verify=False)

		try:
			list_profiles = r.json()
		except ValueError:
			list_profiles = dict()

		list_profiles['status_code'] = r.status_code

		return list_profiles

	def create_storage_capability_profile(self, profile_name=None,
	                                      description=None, qos=None,
	                                      compression=None, deduplication=None,
	                                      encryption=None, iops=None,
	                                      platform=None, space_efficiency=None,
	                                      tiering_policy=None):

		url_action = self.url
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}

		payload = {
			'name': profile_name,
			'description': description,
			'capabilities': {
				'adaptiveQoS': qos,
				'compression': compression,
				'deduplication': deduplication,
				'encryption': encryption,
				'maxThroughputIops': iops,
				'platformType': platform,
				'spaceEfficiency': space_efficiency,
				'tieringPolicy': tiering_policy
				}
		}

		r = requests.post(url=url_action, headers=headers, json=payload, verify=False)

		try:
			create_profile = r.json()
		except ValueError:
			create_profile = dict()

		create_profile['status_code'] = r.status_code

		return create_profile

	def update_storage_capability_profile(self, profile_name=None,
	                                      description=None, qos=None,
	                                      compression=None, deduplication=None,
	                                      encryption=None, iops=None,
	                                      platform=None, space_efficiency=None,
	                                      tiering_policy=None, profile_id=None):

		url_action = self.url
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}

		payload = {
			'storageCapabilityProfile': {
				'name': profile_name,
				'description': description,
				'id': profile_id,
				'capabilities': {
					'adaptiveQoS': qos,
					'compression': compression,
					'deduplication': deduplication,
					'encryption': encryption,
					'maxThroughputIops': iops,
					'platformType': platform,
					'spaceEfficiency': space_efficiency,
					'tieringPolicy': tiering_policy
					}
			}
		}

		r = requests.put(url=url_action, headers=headers, json=payload, verify=False)

		try:
			update_profile = r.json()
		except ValueError:
			update_profile = dict()

		update_profile['status_code'] = r.status_code

		return update_profile

	def delete_storage_capability_profile(self, profile_name=None):
		url_action = self.url
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token,
			'profile-name': profile_name
		}

		r = requests.delete(url=url_action, headers=headers, verify=False)

		try:
			delete_profiles = r.json()
		except ValueError:
			delete_profiles = dict()

		delete_profiles['status_code'] = r.status_code

		return delete_profiles

	def delete_storage_capabilities_by_id(self, profile_id=None):
		api_endpoint = "/" + profile_id
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}

		r = requests.delete(url=url_action, headers=headers, verify=False)

		try:
			delete_profile_id = r.json()
		except ValueError:
			delete_profile_id = dict()

		delete_profile_id['status_code'] = r.status_code

		return delete_profile_id

	def get_storage_capabilities_by_id(self, profile_id=None):
		api_endpoint = "/" + profile_id
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}

		r = requests.get(url=url_action, headers=headers, verify=False)

		try:
			show_profile_id = r.json()
		except ValueError:
			show_profile_id = dict()

		show_profile_id['status_code'] = r.status_code

		return show_profile_id

	def clone_storage_capabilities(self, profile_name=None,
	                                     description=None, qos=None,
	                                     compression=None, deduplication=None,
	                                     encryption=None, iops=None,
	                                     platform=None, space_efficiency=None,
	                                     tiering_policy=None, profile_id=None,
	                                     new_profile_name=None):

		api_endpoint = "/clone"
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}

		payload = {
			"baseProfileName": profile_name,
			"storageCapabilityProfile": {
				"capabilities": {
					"compression": compression,
					"deduplication": deduplication,
					"encryption": encryption,
					"platformType": platform,
					"spaceEfficiency": space_efficiency,
					"tieringPolicy": tiering_policy
					},
				"description": description,
				"id": profile_id,
				"name": new_profile_name
				}
			}

		if not iops:
			payload["storageCapabilityProfile"]["capabilities"]["adaptiveQoS"] = qos.upper()
		else:
			payload["storageCapabilityProfile"]["capabilities"]["maxThroughputIops"] = iops

		r = requests.post(url=url_action, headers=headers, json=payload, verify=False)

		try:
			clone_profile = r.json()
		except ValueError:
			clone_profile = dict()

		clone_profile['status_code'] = r.status_code

		return clone_profile

	def get_storage_capabilities_profile_names(self):
		api_endpoint = "/profile-names"
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}

		r = requests.get(url=url_action, headers=headers, verify=False)

		try:
			show_profile_id = r.json()
		except ValueError:
			show_profile_id = dict()

		show_profile_id['status_code'] = r.status_code

		return show_profile_id
