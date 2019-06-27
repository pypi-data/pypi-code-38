# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=invalid-name, too-few-public-methods
# pylint: disable=too-many-instance-attributes

"""Julia building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import posixpath
import re

import hpccm.config
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell

class julia(bb_base, hpccm.templates.ldconfig, hpccm.templates.rm,
            hpccm.templates.tar, hpccm.templates.wget):
    """The `boost` building block downloads and installs the
    [Boost](https://www.boost.org) component.

    # Parameters

    bootstrap_opts: List of options to pass to `bootstrap.sh`.  The
    default is an empty list.

    ldconfig: Boolean flag to specify whether the Boost library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the Boost library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to building.  For
    Ubuntu, the default values are `bzip2`, `libbz2-dev`, `tar`,
    `wget`, and `zlib1g-dev`.  For RHEL-based Linux distributions the
    default values are `bzip2`, `bzip2-devel`, `tar`, `wget`, `which`,
    and `zlib-devel`.

    prefix: The top level installation location.  The default value
    is `/usr/local/boost`.

    python: Boolean flag to specify whether Boost should be built with
    Python support.  If enabled, the Python C headers need to be
    installed (typically this can be done by adding `python-dev` or
    `python-devel` to the list of OS packages).  The default is False.

    sourceforge: Boolean flag to specify whether Boost should be
    downloaded from SourceForge rather than the current Boost
    repository.  For versions of Boost older than 1.63.0, the
    SourceForge repository should be used.  The default is False.

    version: The version of Boost source to download.  The default
    value is `1.68.0`.

    # Examples

    ```python
    boost(prefix='/opt/boost/1.67.0', version='1.67.0')
    ```

    ```python
    boost(sourceforge=True, version='1.57.0')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(julia, self).__init__(**kwargs)

        self.__baseurl = kwargs.get('baseurl',
                                    'https://julialang-s3.julialang.org/bin/linux/x64')
        self.__cuda = kwargs.get('cuda', False)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__packages = kwargs.get('packages', [])
        self.__prefix = kwargs.get('prefix', '/usr/local/julia')
        self.__version = kwargs.get('version', '1.1.0')

        self.__commands = [] # Filled in by __setup()
        self.__environment_variables = {
            'PATH': '{}:$PATH'.format(posixpath.join(self.__prefix, 'bin'))}
        self.__wd = '/var/tmp' # working directory

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Julia version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        #if self.__packages:
        #    self += environment(
        #        variables={'JULIA_DEPOT_PATH':
        #                   posixpath.join(self.__prefix, 'depot')})
        self += shell(commands=self.__commands)
        if self.__environment_variables:
            self += environment(variables=self.__environment_variables)

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['bzip2', 'libbz2-dev', 'tar', 'wget',
                                     'zlib1g-dev']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['tar', 'wget']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # The download URL has the format MAJOR.MINOR in the path and
        # the tarball contains MAJOR.MINOR.REVISION, so pull apart the
        # full version to get the individual components.
        match = re.match(r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<revision>\d+)',
                         self.__version)
        major_minor = '{0}.{1}'.format(match.groupdict()['major'],
                                       match.groupdict()['minor'])

        tarball = 'julia-{}-linux-x86_64.tar.gz'.format(self.__version)
        url = '{0}/{1}/{2}'.format(self.__baseurl, major_minor, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url,
                                                  directory=self.__wd))
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))

        # "Install"
        self.__commands.append('cp -a {0} {1}'.format(
            posixpath.join(self.__wd, 'julia-{}'.format(self.__version)),
            self.__prefix))

        # Install packages
        if self.__cuda:
            self.__packages.extend(['CUDAnative', 'CuArrays', 'GPUArrays',
                                    'Knet'])
        if self.__packages:
            # remove duplicates
            self.__packages = sorted(list(set(self.__packages)))
            #for pkg in self.__packages:
                #self.__commands.append('{0} -e \'import Pkg; Pkg.add("{1}")\''.format(posixpath.join(self.__prefix, 'bin', 'julia'), pkg))
            packages_str = ', '.join('"{}"'.format(pkg) for pkg in self.__packages)
            self.__commands.append('{0} -e \'import Pkg; Pkg.add([{1}])\''.format(posixpath.join(self.__prefix, 'bin', 'julia'), packages_str))

        # Set library path
        libpath = posixpath.join(self.__prefix, 'lib')
        if self.ldconfig:
            self.__commands.append(self.ldcache_step(directory=libpath))
        else:
            self.__environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(libpath)

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd, 'julia-{}'.format(self.__version))]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        b = boost(...)
        Stage0 += b
        Stage1 += b.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('Julia'))
        instructions.append(copy(_from=_from, src=self.__prefix,
                                 dest=self.__prefix))
        if self.ldconfig:
            instructions.append(shell(
                commands=[self.ldcache_step(
                    directory=posixpath.join(self.__prefix, 'lib'))]))
        if self.__environment_variables:
            instructions.append(environment(
                variables=self.__environment_variables))
        return '\n'.join(str(x) for x in instructions)
