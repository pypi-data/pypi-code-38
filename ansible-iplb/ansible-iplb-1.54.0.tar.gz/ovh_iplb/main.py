#!/usr/bin/python
# -*- encoding: utf-8 -*-
# This is the that get copied on ansible module
# The aim of this file is to avoid modifying it
# We should always modify module_def.py instead
from ovh_iplb import module_def

# This import seems to do magic trick and MUST be imported in main
# this is the reason why it's imported here and passed to module_def.main
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type


ANSIBLE_METADATA = module_def.ANSIBLE_METADATA

DOCUMENTATION = module_def.DOCUMENTATION

EXAMPLES = module_def.EXAMPLES

RETURN = module_def.RETURN


if __name__ == '__main__':
    module_def.main(AnsibleModule)
