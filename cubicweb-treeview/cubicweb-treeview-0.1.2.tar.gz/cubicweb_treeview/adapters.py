# copyright 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.

__docformat__ = "restructuredtext en"

from cubicweb.entities.adapters import ITreeAdapter


class TVITreeAdapter(ITreeAdapter):
    def is_editable_leaf(self):
        return len(self.same_type_children()) == 0

    def editable_children(self, entities=False):
        return self.same_type_children(entities=entities)


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (TVITreeAdapter,))
    vreg.register_and_replace(TVITreeAdapter, ITreeAdapter)
