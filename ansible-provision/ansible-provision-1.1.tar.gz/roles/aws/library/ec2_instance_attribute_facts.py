
#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
'''

EXAMPLES = ''''''

import traceback

try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ec2 import (ansible_dict_to_boto3_filter_list,
                                      boto3_conn, boto3_tag_list_to_ansible_dict, camel_dict_to_snake_dict,
                                      ec2_argument_spec, get_aws_connection_info)


def get_instance_attribute(connection, module):

    instance_id = module.params.get("instance_id")
    attribute = module.params.get('attribute')
    response = connection.describe_instance_attribute(Attribute=attribute,InstanceId=instance_id)
    module.exit_json(attributes=response)


def main():

    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            instance_id=dict(required=True),
            attribute=dict(required=True)
        )
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True
                           )

    if not HAS_BOTO3:
        module.fail_json(msg='boto3 required for this module')

    region, ec2_url, aws_connect_params = get_aws_connection_info(module, boto3=True)

    if region:
        connection = boto3_conn(module, conn_type='client', resource='ec2', region=region, endpoint=ec2_url, **aws_connect_params)
    else:
        module.fail_json(msg="region must be specified")

    get_instance_attribute(connection, module)


if __name__ == '__main__':
    main()