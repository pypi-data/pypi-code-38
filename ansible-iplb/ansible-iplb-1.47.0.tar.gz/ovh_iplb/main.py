#!/usr/bin/python
# -*- encoding: utf-8 -*-
# This is the that get copied on ansible module
# The aim of this file is to avoid modifying it
# We should always modify module_def.py instead
from ovh_iplb import module_def

__metaclass__ = type


ANSIBLE_METADATA = module_def.ANSIBLE_METADATA

DOCUMENTATION = module_def.DOCUMENTATION

EXAMPLES = module_def.EXAMPLES

RETURN = module_def.RETURN


if __name__ == '__main__':
    module_def.main()
