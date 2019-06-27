#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import platform
from conans.client.conan_api import Conan
from sesame import build_shared

import cpt.builds_generator

def get_builder(shared_option_name=None,
                pure_c=True,
                dll_with_static_runtime=False,
                build_policy=None,
                build_types=None):

    builder = build_shared.get_builder(build_policy, build_types)
    builder.add_common_builds(
        shared_option_name=shared_option_name,
        pure_c=pure_c,
        dll_with_static_runtime=dll_with_static_runtime)

    return builder
