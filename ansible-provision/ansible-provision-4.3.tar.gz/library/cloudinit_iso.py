#!/usr/bin/python
DOCUMENTATION = '''
module: cloudinit_iso
author:
    - "Moshe Immerman"
short_description:  Creates an ISO image containing cloud-init user-data files
description:
    -  Creates an ISO image containing cloud-init user-data files
options:
    dest:
        required: True
        description: ['']
    user:
        required: True
        description: ['']
    type:
        required: False
        default: vmware
        description: The type of cloud-init ISO to create, Valid values are: vmware,coreos
    meta:
        required: True
        description: ['']
'''
EXAMPLES = '''
     - cloudinit_iso:
          dest: /tmp/cloudinit.iso
          type: vmware
          user: |
            "
'''
import os.path
from subprocess import check_call
from ansible.module_utils.basic import AnsibleModule
import os, sys
import uuid
from tempfile import gettempdir

def log(s):
    sys.stderr.write("%s\n" % s)

def main():
    arg_spec = dict(
        dest=dict(required=True),
        user=dict(required=True),
        meta=dict(required=False),
        type=dict(required=False,default="vmware")
    )
    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    tmp = os.path.join(gettempdir(), '{}'.format(hash(os.times())))
    log("Writing temp user-data.txt: " + tmp)
    os.makedirs(tmp)

    path = "/user-data"
    if module.params['type'] == 'coreos':
        os.makedirs(tmp + "/openstack/latest")
        path = "/openstack/latest/user_data"

    with open(tmp + path, 'w') as f:
        f.write(module.params['user'])
    with open(tmp + "/meta-data", "w") as f:
        f.write('instance-id: i%s\n' % uuid.uuid1())

        if 'meta' in module.params and module.params['meta'] is not None:
            f.write(module.params['meta'])
        else:
            f.write('local-hostname: cloudy')

    if module.params['type'] == 'coreos':
       check_call("mkisofs -output %s -volid config-2 -joliet -rock ." % module.params['dest'], shell=True,cwd=tmp)
    else:
        check_call("mkisofs -output %s -volid cidata -joliet -rock user-data meta-data" % module.params['dest'], shell=True,cwd=tmp)

    module.exit_json(changed=True)


if __name__ == '__main__':
    main()