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

import os
import requests
import productmd.common


class PungiCompose(object):
    """Represents 3rd party Pungi Compose"""

    def __init__(self, variant_url):
        """
        Creates new PungiCompose.

        :param str metadata_url: URL to Pungi variant repository directory.
        """
        # The `variant_url` is for example "http://localhost/foo/compose/Server".
        self.variant_url = variant_url.rstrip("/")
        # The `variant_name` is for example `Server`
        self.variant_name = os.path.basename(self.variant_url)
        # The `metadata_url` is for example "http://localhost/foo/compose/metadata".
        self.metadata_url = os.path.join(
            os.path.dirname(self.variant_url), "metadata")

    def _fetch_json(self, url):
        """
        Fetches the json file represented by `url`.
        """
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    def get_rpms_data(self):
        """
        Returns the data describing the RPMs in the pungi compose.
        :rtype: dict.
        :return: Dictionary with RPMs data in following format:
            {
                "sigkeys": set() with sigkeys used in the compose.
                "arches": set() with all the arches used in the compose.
                "builds": {
                    koji-build-nvr1: set() with the RPMs NEVRAs,
                    koji-build-nvr2: ...,
                    ...
                }
            }
        """
        ret = {}
        ret["sigkeys"] = set()
        ret["arches"] = set()
        ret["builds"] = {}

        # Fetch the rpms.json and get the part containing SRPMs
        # for the right variant.
        url = os.path.join(self.metadata_url, "rpms.json")
        data = self._fetch_json(url)
        srpms_per_arch = data.get("payload", {}).get("rpms", {}).get(
            self.variant_name)
        if not srpms_per_arch:
            raise ValueError("The %s does not contain payload -> rpms -> %s "
                             "section" % (url, self.variant_name))

        # Go through the data and fill in the dict to return.
        for arch, srpms in srpms_per_arch.items():
            ret["arches"].add(arch)
            for srpm_nevra, rpms in srpms.items():
                packages = set()
                for rpm_nevra, rpm_data in rpms.items():
                    packages.add(rpm_nevra)
                    ret["sigkeys"].add(rpm_data["sigkey"])

                srpm_nvr = "{name}-{version}-{release}".format(
                    **productmd.common.parse_nvra(srpm_nevra))
                ret["builds"][srpm_nvr] = packages

        return ret
