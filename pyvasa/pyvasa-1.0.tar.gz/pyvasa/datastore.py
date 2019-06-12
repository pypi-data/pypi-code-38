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


class Datastore(object):
	def __init__(self, port=None, url=None, token=None, api_version='1.0'):
		self.api = api_version
		self.port = str(port)
		self.url = "https://" + url + ":" + self.port + "/api/rest/" + self.api + "/admin/datastore"

		if token is not None:
			self.token = token

	def mount_datastore_on_host(self, container_id=None, ds_name=None, ds_type=None, host_id=None):
		api_endpoint = "/mount-on-host"
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}

		payload = {
			'containerId': container_id,
			'datastoreName': ds_name,
			'datastoreType': ds_type,
			'hostMoref': host_id
			}

		r = requests.put(url=url_action, headers=headers, json=payload, verify=False)

		try:
			mount = r.json()
		except ValueError:
			mount = dict()

		mount['status_code'] = r.status_code

		return mount

	def mount_datastore_on_additional_hosts(self, ds_name=None, ds_type=None, host_ids=None):
		api_endpoint = "/mount-on-additional-hosts"
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}

		payload = {
			'datastoreName': ds_name,
			'datastoreType': ds_type,
			'hostMoref': [
				host_ids
			]
		}

		r = requests.put(url=url_action, headers=headers, json=payload, verify=False)

		try:
			mounts = r.json()
		except ValueError:
			mounts = dict()

		mounts['status_code'] = r.status_code

		return mounts

	def unmount_datastore(self, ds_moref=None, ds_type=None, host_ids=None):
		api_endpoint = "/unmount"
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}

		payload = {
			'datastoreMoref': ds_moref,
			'datastoreType': ds_type,
			'hostMoref': [
				host_ids
			]
		}

		r = requests.put(url=url_action, headers=headers, json=payload, verify=False)

		try:
			umount = r.json()
		except ValueError:
			umount = dict()

		umount['status_code'] = r.status_code

		return umount

	def create_datastore(self, cluster_ip=None, ds_type=None, scp=None, description=None, flexvol=None,
	                     ds_name=None, protocol=None, target=None, vserver=None):
		url_action = self.url
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token
		}
		"""
		flexvol must have a dict. eg.: 
			flexvol:
				'vvol_01': 'scp_gold'
		"""
		payload = {
			"clusterIp": cluster_ip,
			"dataStoreType": ds_type,
			"defaultSCP": scp,
			"description": description,
			"flexVolSCPMap": flexvol,
			"name": ds_name,
			"protocol": protocol,
			"targetMoref": target,
			"vserverName": vserver
		}

		r = requests.post(url=url_action, headers=headers, json=payload, verify=False)

		try:
			ds_create = r.json()
		except ValueError:
			ds_create = dict()

		ds_create['status_code'] = r.status_code

		return ds_create

	def delete_datastore(self, ds_type=None, ds_moref=None):
		url_action = self.url
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token,
			'datastore-type': ds_type,
			'datastore-moref': ds_moref
		}

		r = requests.delete(url=url_action, headers=headers, verify=False)

		try:
			ds_delete = r.json()
		except ValueError:
			ds_delete = dict()

		ds_delete['status_code'] = r.status_code

		return ds_delete

	def get_datastore(self, ds_type=None, ds_name=None):
		url_action = self.url
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token,
			'datastore-type': ds_type,
			'name': ds_name
		}

		r = requests.get(url=url_action, headers=headers, verify=False)

		try:
			ds_details = r.json()
		except ValueError:
			ds_details = dict

		ds_details['status_code'] = r.status_code

		return ds_details

	def get_datastore_clusters(self, scp=None, protocol=None):
		api_endpoint = "/clusters"
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token,
			'profile-names': scp,
			'protocol': protocol
		}

		r = requests.get(url=url_action, headers=headers, verify=False)

		try:
			ds_cfilter = r.json()
		except ValueError:
			ds_cfilter = dict()

		ds_cfilter['status_code'] = r.status_code

		return ds_cfilter

	def get_aggregates_for_scp(self, scp=None, cluster=None, vserver=None):
		api_endpoint = "/provisioning/aggregates/forscp"
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token,
			'profile-names': scp,
			'cluster': cluster,
			'vserver-name': vserver
		}

		r = requests.get(url=url_action, headers=headers, verify=False)

		try:
			ds_afilter = r.json()
		except ValueError:
			ds_afilter = dict()

		ds_afilter['status_code'] = r.status_code

		return ds_afilter

	def add_storage(self, ds_type=None, ds_name=None, cluster_ip=None, scp=None, volume=None, vserver=None):
		api_endpoint = "/storage"
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token,
			'datastore-type': ds_type
		}

		payload = {
			"clusterIP": cluster_ip,
			"datastoreName": ds_name,
			"flexVolSCPNames": [
				{
					"flexVolName": volume,
					"scpName": scp
				}
			],
			"vserverName": vserver
		}

		r = requests.put(url=url_action, headers=headers, json=payload, verify=False)

		try:
			s_add = r.json()
		except ValueError:
			s_add = dict()

		s_add['status_code'] = r.status_code

		return s_add

	def delete_storage(self, ds_type=None, ds_name=None, volume=None):
		api_endpoint = "/storage"
		url_action = self.url + api_endpoint
		headers = {
			'Accept': 'application/json',
			'vmware-api-session-id': self.token,
			'datastore-name': ds_name,
			'datastore-type': ds_type,
			'flex-vol-names': volume
		}

		r = requests.delete(url=url_action, headers=headers, verify=False)

		try:
			s_delete = r.json()
		except ValueError:
			s_delete = dict()

		s_delete['status_code'] = r.status_code

		return s_delete
