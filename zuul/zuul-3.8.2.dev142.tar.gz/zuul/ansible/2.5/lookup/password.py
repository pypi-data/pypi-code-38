# Copyright 2019 OpenStack Foundation
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.


from zuul.ansible import paths
password = paths._import_ansible_lookup_plugin("password")


class LookupModule(password.LookupModule):

    def run(self, terms, variables, **kwargs):
        for term in terms:
            relpath = password._parse_parameters(term)[0]
            # /dev/null is whitelisted because it's interpreted specially
            if relpath != "/dev/null":
                path = self._loader.path_dwim(relpath)
                paths._fail_if_unsafe(path, allow_trusted=True)
        return super(LookupModule, self).run(terms, variables, **kwargs)
