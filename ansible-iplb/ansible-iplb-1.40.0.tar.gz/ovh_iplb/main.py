#!/usr/bin/python
# -*- encoding: utf-8 -*-

from ovh_iplb.iplb_client import IPLB

from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = """
---
module: ovh_ip_loadbalancing_backend
short_description: Manage OVH IP LoadBalancing backends (called farms) and its server
description:
    - Manage OVH (French European hosting provider) LoadBalancing IP backends
version_added: "0.0"
author: Luc DUZAN, Sébastien Jardin
notes:
    - Uses the python OVH Api (https://github.com/ovh/python-ovh).
      You have to create an application (a key and secret) with a consummer
      key as described into (https://eu.api.ovh.com/g934.first_step_with_api)
requirements:
    - ovh >  0.3.5
options:
    application_key:
        required: true
        description: See (https://eu.api.ovh.com/createApp/) for more information about how to generate it
    application_secret:
        required: true
        description: See (https://eu.api.ovh.com/createApp/) for more information about how to generate it
    consumer_key:
        required: true
        description: See (https://eu.api.ovh.com/createApp/) for more information about how to generate it
    endpoint:
        required: true
        choices: ['ovh-eu', 'ovh-us', 'ovh-ca', 'soyoustart-eu', 'soyoustart-ca', 'kimsufi-eu', 'kimsufi-ca']
        description: Which ovh endpoint to use
    iplblId:
        required: true
        description: ID of the LoadBalancing (loadbalancer-XXXXXXXXXXXXXx)
    timeout:
        default: 120
        type: int
        description: How long should we wait in second when refreshing IPLB configuration before failing
    farms:
        description: list of farm managed by ansible in your IPLB
        type: list
        default: []
        options:
            name:
                type: string
                required: true
                description: >
                    The name of your farm. If not farm exists with such name, it will be created
                    If a farm with such name exists, it will be modified.
                    If more than one farm with such name exist, it will fail
            id:
                type: integer
                description: >
                    ID of a farm (not recommanded please use name if you can).
                    If you use an ID, please make sure the farm already exist.
            type:
                required: true
                choices: ['roundrobin', 'first', 'leastconn', 'uri', 'source']
                description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
            port:
                type: integer
                required: true
                description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
            probe:
                type: dict
                description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                options:
                    type:
                         choices: ['internal', 'mysql', 'oco', 'pgsql', 'smtp', 'tcp']
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                    forceSsl:
                         type: bool
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                    interval:
                         type: int
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                    method:
                         type: int
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                         choices: ['GET', 'HEAD', 'OPTIONS', 'internal']
                    negate:
                         type: bool
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                    pattern:
                         type: string
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                    url:
                         type: string
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                    port:
                         type: int
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
            servers:
                type: list
                description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                options:
                    address:
                         type: string
                         required: True
                         description: Ip or dns of your server. This module will also handle address has ID
                    backup:
                         type: bool
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                    chain:
                         type: string
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                    display_name:
                         type: string
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                    port:
                         type: int
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                    probe:
                         type: bool
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                    proxy_protocol_version:
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                         choices: ['v1', 'v2', 'v2-ssl', 'v2-ssl-cn']
                    ssl:
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                         type: bool
                    status:
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                         choices: ['active', 'inactive']
                    weight:
                         description: Please refer to https://docs.ovh.com/gb/en/load-balancer/
                         type: int
"""

EXAMPLES = """
  ovh_iplb:
    iplb_id: 'loadbalancer-c6f9b9aa43f6cc17bd51964011f48d76'
    timeout: 120
    endpoint: '{{ ovh_credentials.endpoint }}'
    application_key: '{{ ovh_credentials.application_key }}'
    application_secret: '{{ ovh_credentials.application_secret }}'
    consumer_key: '{{ ovh_credentials.consumer_key }}'
    farms:
      - name: test_dev_ansible_3
        type: tcp
        port: 4242
        zone: all
        servers:
          - address: 10.11.3.4
            backup: true
            displayName: "Luca"
            status: "active"
            weight: 4
"""

RETURN = """
changed:
    type: bool
    description: True if IPLB conf has been modified or/and IPLB conf has been refresh
"""


def main():
    module = AnsibleModule(
        argument_spec={
            'application_key': {'no_log': True,
                                'required': True},

            'application_secret': {'no_log': True,
                                   'required': True},

            'consumer_key': {'no_log': True,
                             'required': True},

            'endpoint': {'required': True,
                         'choices': ['ovh-eu', 'ovh-us', 'ovh-ca', 'soyoustart-eu',
                                     'soyoustart-ca', 'kimsufi-eu', 'kimsufi-ca']},

            'iplb_id': {'required': True},

            'timeout': {'default': 120, 'type': 'int'},

            'frontends': {
                'type': 'list',
                'default': [],
                'elements': 'dict',
                'options': {
                    'id':  {'type': 'int'},
                    'type': {'required': True, 'choices': ['tcp', 'http', 'udp']},
                    'allowed_source': {'type': 'str'},
                    'dedicated_ipfo': {'type': 'str'},
                    'default_farm_id': {'type': 'int'},
                    'default_farm_name': {'type': 'str'},
                    'default_ssl_id': {'type': 'int'},
                    'disabled': {'default': 'False', 'type': 'bool'},
                    'name': {'type': 'str'},
                    'hsts': {'type': 'bool'},
                    'http_header': {'type': 'str'},
                    'port': {'required': True, 'type': 'str'},
                    'redirect_location': {'type': 'str'},
                    'ssl': {'default': 'False', 'type': 'bool'},
                    'zone': {'choices': ['rbx', 'gra', 'sbg', 'bhs', 'all'],
                             'default': 'all'}
                }
            },
            'farms': {
                'type': 'list',
                'default': [],
                'elements': 'dict',
                'options': {
                    'id': {'type': 'int'},
                    'type': {'required': True, 'choices': ['tcp', 'http', 'udp']},
                    'name': {'required': True, 'type': 'str'},
                    'port': {'type': 'int'},
                    'balance': {'default': 'roundrobin',
                                'choices': ['roundrobin', 'first', 'leastconn', 'uri', 'source']},
                    'zone': {'choices': ['rbx', 'gra', 'sbg', 'bhs', 'all'],
                             'default': 'all'},

                    'stickiness': {'choices': ['cookie', 'sourceIp']},
                    'vrack_network_id': {'type': 'int'},
                    'probe': {
                        'type': 'dict',
                        'options': {
                            'type': {'choices': ['internal', 'mysql', 'oco', 'pgsql', 'smtp', 'tcp']},
                            'forceSsl': {'type': 'bool'},
                            'interval': {'type': 'int'},
                            'method': {'choices': ['GET', 'HEAD', 'OPTIONS', 'internal']},
                            'match': {'choices': ['internal', 'matches', 'status']},
                            'negate': {'type': 'bool'},
                            'pattern': {'type': 'str'},
                            'url': {'type': 'str'},
                            'port': {'type': 'int'},
                        }
                    },
                    'servers': {
                        'type': 'list',
                        'elements': 'dict',
                        'default': [],
                        'options': {
                            'address': {'type': 'str', 'required': True},
                            'backup': {'type': 'bool', 'default': False},
                            'chain': {'type': 'str'},
                            'display_name': {'type': 'str'},
                            'port':  {'type': 'int'},
                            'probe': {'type': 'bool'},
                            'proxy_protocol_version': {'choices': ['v1', 'v2', 'v2-ssl', 'v2-ssl-cn']},
                            'ssl': {'type': 'bool'},
                            'status': {'choices': ['active', 'inactive'], 'default': 'active'},
                            'weight': {'type': 'int'},
                        }
                    }
                }
            },
        }
    )

    try:
        changed = IPLB(module.params).apply()
    except BaseException as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
