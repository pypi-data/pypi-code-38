# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Filip Valder <fvalder@redhat.com>

import pkg_resources

from module_build_service import conf
from module_build_service.resolver.base import GenericResolver

# NOTE: if you are adding a new resolver to MBS please note that you also have to add
# a new resolver to your setup.py and update you egg-info
for entrypoint in pkg_resources.iter_entry_points("mbs.resolver_backends"):
    GenericResolver.register_backend_class(entrypoint.load())

if not GenericResolver.backends:
    raise ValueError("No resolver plugins are installed or available.")

# Config has the option of which resolver should be used for current MBS run.
# Hence, create a singleton system wide resolver for use. However, resolver
# could be created with other required arguments in concrete cases.
system_resolver = GenericResolver.create(conf)
