#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright, (c) 2018, Ansible Project
# Copyright, (c) 2018, Moshe Immerman

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION = '''
'''
EXAMPLES = '''
'''

RETURN = """
"""

try:
    from pyVmomi import vim
except ImportError:
    pass

from ansible.module_utils.basic import AnsibleModule
import os
import sys
import urllib3
import logging
import requests
import json
logger = logging.getLogger('vmware')
hdlr = logging.FileHandler('/tmp/ansible-vmware.log')
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
urllib3.disable_warnings()
from requests.auth import HTTPBasicAuth
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}



def to_dict(attributes):
    return {item['name'] : item['value'] for item in attributes}


class vRO:

    def __init__(self, host, username, password, verify=False):
        self.host = "https://" + host
        self.verify = verify
        self.username = username
        self.password = password

    def auth(self):
        return HTTPBasicAuth(self.username, self.password)

    def get(self, url, params={}):
        if not url.startswith('http'):
            url = self.host + "/" + url

        return requests.get(url,
            auth = self.auth(),
            params = params,
            verify = self.verify,
            headers = headers
        )

    def post(self, url, body):
        return requests.post(self.host + "/" + url,
            auth = self.auth(),
            data=json.dumps(body),
            verify = self.verify,
            headers = headers
        )

    def get_vcac_id(self):
        host = self.get("vco/api/catalog/vCAC/VCACHost").json()
        return to_dict(host['link'][0]['attributes'])['id']

    def get_reservations(self):
        return self.get('vco/api/inventory/vCAC/VCACHost/{id}/virtualFolder_Reservations/{id}%252FReservations/'.format(id=self.get_vcac_id()))

    def get_business_groups(self):
        return self.get('vco/api/inventory/vCAC/VCACHost/{id}/virtualFolder_ProvisioningGroups/{id}%252FProvisioningGroups/'.format(id=self.get_vcac_id()))


class Workflow:

    def __init__(self, r, name):
        self.r = r
        self.name = name
        self.results = None
        results = r.get("vco/api/workflows", {"conditions": "name=" + name})
        logger.info(str(results.status_code)  + "\n" + results.text)
        if results.status_code != 200:
            raise Exception(results.text)

        for attribute in json.loads(results.text)['link'][0]['attributes']:
            if attribute['name'] == 'id':
                self.id = attribute['value']
        results = r.get("vco/api/workflows/" + self.id)
        self.params = {}
        for param in  json.loads(results.text)["input-parameters"]:
            self.params[param['name']] = param

    def execute(self, params):
        if self.results != None:
            return self.results
        body = []
        for param in params:

            t = self.params[param]['type']
            p = { "scope": "local", "name": param, "type": t }
            if ":" not in t:
                value = {}
                value[t] = {
                    "value": params[param]
                }
                p['value'] = value

            else:
                p['value'] = {
                     "sdk-object" : {
                         "type" : t,
                          "id" :params[param]
                    }
                }

            body.append(p)
        res = self.r.post("vco/api/workflows/%s/executions" % self.id, {"parameters": body})
        if 'Location' in res.headers:
            res = self.r.get(res.headers['Location'])
        return res


def main():
    argument_spec = dict(
        hostname=dict(type='str', required=True),
        username=dict(type='str',required=True),
        password=dict(type='str',required=True,no_log=True),
        workflow=dict(type='str',required=True),
        params=dict(type='dict',required=True)
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False
    )

    vro = vRO(module.params['hostname'],module.params['username'], module.params['password'])
    workflow = Workflow(vro, module.params['workflow'])
    logger.info("Executing %s with %s" % (workflow.name, module.params))
    result = workflow.execute(module.params['params'])
    logger.info("Executed %s with result =>  %s \n %s" % (workflow.name, result.status_code, result.text))
    if result.status_code == 200:
        module.exit_json(status_code=200, result=result.json())
    else:
        try:
            module.fail_json(msg=result.json()['message'], url=result.url)
        except:
             module.fail_json(msg="Unknown error executing workflow", response=response.text, url=result.url)


if __name__ == '__main__':
    main()
