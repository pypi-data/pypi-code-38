# -*- coding: utf-8 -*-
# Copyright (c) 2019  Red Hat, Inc.
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
# Written by Jan Kaluza <jkaluza@redhat.com>

from module_build_service.resolver.DBResolver import DBResolver


class LocalResolver(DBResolver):
    """
    Resolver using DNF and local repositories.

    It is subclass of DBResolver with small changes to DBResolver logic to fit
    the offline local module builds. See particular methods for more information.
    """

    backend = "local"

    def get_buildrequired_modulemds(self, name, stream, base_module_nsvc):
        """
        Returns modulemd metadata of all module builds with `name` and `stream`.

        For LocalResolver which is used only for Offline local builds,
        the `base_module_nsvc` is ignored. Normally, the `base_module_nsvc is used
        to filter out platform:streams which are not compatible with currently used
        stream version. But during offline local builds, we always have just single
        platform:stream derived from PLATFORM_ID in /etc/os-release.

        Because we have just single platform stream, there is no reason to filter
        incompatible streams. This platform stream is also expected to not follow
        the "X.Y.Z" formatting which is needed for stream versions.

        :param str name: Name of module to return.
        :param str stream: Stream of module to return.
        :param str base_module_nsvc: Ignored in LocalResolver.
        :rtype: list
        :return: List of modulemd metadata.
        """
        return self.get_module_modulemds(name, stream)
