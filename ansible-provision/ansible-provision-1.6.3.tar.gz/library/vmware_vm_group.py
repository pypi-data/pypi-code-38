#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright, (c) 2018, Ansible Project
# Copyright, (c) 2018, Moshe Immerman
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
from ansible.module_utils.vmware import PyVmomi, vmware_argument_spec,find_cluster_by_name,wait_for_task


import logging

logger = logging.getLogger('vmware')
hdlr = logging.FileHandler('/tmp/ansible-vmware.log')
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class VmGroupManager(PyVmomi):
    def __init__(self, module):
        super(VmGroupManager, self).__init__(module)

    def modify_groups(self, vm, groups):
        changed = False
        cluster = find_cluster_by_name(self.content, self.module.params['cluster'])

        for group in cluster.configurationEx.group:
          logger.info(group.name)
          for _group in groups:
            if group.name == _group:
             if vm not in group.vm:
                logger.info("Adding %s to %s", vm.name, group.vm)
                group.vm.append(vm)
                spec = vim.cluster.ConfigSpecEx(groupSpec=[vim.cluster.GroupSpec(info=group,operation="edit")])
                wait_for_task(cluster.ReconfigureEx(spec=spec, modify=True))
                changed = True

        return {'changed': changed, 'failed': False, 'groups': groups}



def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        datacenter=dict(type='str'),
        cluster=dict(type='str'),
        name=dict(required=False, type='str'),
        folder=dict(type='str'),
        uuid=dict(type='str'),
        groups=dict(
            type='list',
            default=[]
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[['name', 'uuid']],
    )

    if module.params.get('folder'):
        # FindByInventoryPath() does not require an absolute path
        # so we should leave the input folder path unmodified
        module.params['folder'] = module.params['folder'].rstrip('/')

    pyv = VmGroupManager(module)
    results = {'changed': False, 'failed': False, 'instance': dict()}

    # Check if the virtual machine exists before continuing
    vm = pyv.get_vm()

    if vm:
        results = pyv.modify_groups(vm, module.params['groups'])
        module.exit_json(**results)
    else:
        # virtual machine does not exists
        module.fail_json(msg="Unable to manage vm group membership for non-existing"
                             " virtual machine %s" % (module.params.get('name') or module.params.get('uuid')))


if __name__ == '__main__':
    main()