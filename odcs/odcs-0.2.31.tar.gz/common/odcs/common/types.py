# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>


class PungiSourceType:
    KOJI_TAG = 1
    MODULE = 2
    REPO = 3
    PULP = 4
    RAW_CONFIG = 5
    BUILD = 6
    PUNGI_COMPOSE = 7


PUNGI_SOURCE_TYPE_NAMES = {
    "tag": PungiSourceType.KOJI_TAG,
    "module": PungiSourceType.MODULE,
    "repo": PungiSourceType.REPO,
    # This is not real PungiSourceType, but ODCS handles the PULP
    # as a extra source type by generating the .repo file pointing
    # to composes done by PULP/PUB.
    "pulp": PungiSourceType.PULP,
    # This allows to submit raw pungi config from predefined URLs in ODCS
    # server-side configuration.
    "raw_config": PungiSourceType.RAW_CONFIG,
    # Generates compose using exactly defined set of Koji builds without
    # pulling in RPMs from any Koji tag.
    "build": PungiSourceType.BUILD,
    # Generates compose using the same set of RPMs as in existing 3rd party
    # Pungi compose.
    "pungi_compose": PungiSourceType.PUNGI_COMPOSE,
}

INVERSE_PUNGI_SOURCE_TYPE_NAMES = {
    v: k for k, v in PUNGI_SOURCE_TYPE_NAMES.items()}

COMPOSE_STATES = {
    # Compose is waiting to be generated
    "wait": 0,
    # Compose is being generated.
    "generating": 1,
    # Compose is generated - done.
    "done": 2,
    # Compose has been removed.
    "removed": 3,
    # Compose generation has failed.
    "failed": 4,
}

INVERSE_COMPOSE_STATES = {v: k for k, v in COMPOSE_STATES.items()}

MULTILIB_METHODS = {
    "none": 0,
    # Packages whose name ends with "-devel" or "-static" suffix will
    # be considered as multilib.
    "runtime": 1,
    # Packages that install some shared object file "*.so.*" will be
    # considered as multilib.
    "devel": 2,
    # All pakages will be considered as multilib.
    "all": 4,
}

INVERSE_MULTILIB_METHODS = {v: k for k, v in MULTILIB_METHODS.items()}

COMPOSE_RESULTS = {
    "repository": 1,
    "iso": 2,
    "ostree": 4,
    "boot.iso": 8,
}

COMPOSE_FLAGS = {
    "no_flags": 0,
    # Compose without pulling-in the dependencies of packages or modules
    # defined for a compose.
    "no_deps": 1,
    # Compose without pulling-in packages from the parent Koji tags.
    "no_inheritance": 2,
    # For "pulp" source_type, include unpublished Pulp repos.
    "include_unpublished_pulp_repos": 4,
    # Abort the compose when some package has broken dependencies.
    "check_deps": 8,
}

INVERSE_COMPOSE_FLAGS = {v: k for k, v in COMPOSE_FLAGS.items()}
