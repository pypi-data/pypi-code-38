# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-seda views for ArchiveUnit"""

from cubicweb import _
from cubicweb.predicates import adaptable, is_instance
from cubicweb.web import component

from ..entities import simplified_profile, component_unit
from ..entities.itree import move_child_at_index, reparent
from . import jqtree


class BaseTreeComponent(component.EntityCtxComponent):
    """Display the whole profile tree."""
    __regid__ = 'seda.tree'
    __select__ = (component.EntityCtxComponent.__select__
                  & adaptable('ITreeBase'))
    __abstract__ = True
    context = 'left'
    order = -1

    def render_body(self, w):
        self._cw.add_css('cubes.jqtree.css')
        self._cw.add_js('cubes.seda.js')
        self.entity.view('jqtree.treeview', w=w)


class ProfileTreeComponent(BaseTreeComponent):
    __select__ = (
        BaseTreeComponent.__select__
        & is_instance(
            'SEDAArchiveTransfer',
            'SEDAArchiveUnit',
            'SEDABinaryDataObject',
            'SEDAPhysicalDataObject',
        )
    )
    title = _('SEDA profile tree')


class UnitTreeComponent(BaseTreeComponent):
    __select__ = BaseTreeComponent.__select__ & component_unit()
    title = _('Archive unit component tree')


class SEDAIJQTreeAdapter(jqtree.IJQTreeAdapter):
    js_can_move_to = 'seda.canMoveTo'


class ArchiveTransferIJQTreeAdapter(SEDAIJQTreeAdapter):
    __select__ = (SEDAIJQTreeAdapter.__select__
                  & is_instance('SEDAArchiveTransfer'))

    def maybe_parent_of(self):
        return ['SEDAArchiveUnit',
                'SEDAPhysicalDataObject', 'SEDABinaryDataObject']

    def move_child_at_index(self, ceid, index, reparenting=False):
        move_child_at_index(self._cw, self.entity.eid, ceid, index, reparenting)


class SimplifiedArchiveTransferIJQTreeAdapter(ArchiveTransferIJQTreeAdapter):
    __select__ = ArchiveTransferIJQTreeAdapter.__select__ & simplified_profile()

    def maybe_parent_of(self):
        return ['SEDAArchiveUnit']


class ArchiveUnitIJQTreeAdapter(SEDAIJQTreeAdapter):
    __select__ = (SEDAIJQTreeAdapter.__select__
                  & is_instance('SEDAArchiveUnit'))

    def maybe_parent_of(self):
        return [] if self.entity.is_archive_unit_ref else ['SEDAArchiveUnit']

    def maybe_moved(self):
        return True

    def reparent(self, peid, index):
        parent = self._cw.entity_from_eid(peid)
        if parent.cw_etype == 'SEDAArchiveUnit':
            parent = parent.first_level_choice.content_sequence
        else:
            assert parent.cw_etype == 'SEDAArchiveTransfer', (
                'cannot re-parent to entity type {0}'.format(parent.cw_etype))
        reparent(self.entity, parent.eid, index)

    def move_child_at_index(self, ceid, index, reparenting=False):
        move_child_at_index(self._cw,
                            self.entity.first_level_choice.content_sequence.eid,
                            ceid, index, reparenting)


class SimplifiedArchiveUnitIJQTreeAdapter(ArchiveUnitIJQTreeAdapter):
    __select__ = ArchiveUnitIJQTreeAdapter.__select__ & simplified_profile()

    def maybe_parent_of(self):
        return [] if self.entity.is_archive_unit_ref else ['SEDAArchiveUnit',
                                                           'SEDABinaryDataObject']

    def move_child_at_index(self, ceid, index, reparenting=False):
        # when reordering a data object, we actually have to maintain ordering
        # of its reference
        child = self._cw.entity_from_eid(ceid)
        if child.cw_etype == 'SEDABinaryDataObject':
            child = child.reverse_seda_data_object_reference_id[0]
        move_child_at_index(self._cw,
                            self.entity.first_level_choice.content_sequence.eid,
                            child.eid, index, reparenting)


class DataObjectIJQTreeAdapter(SEDAIJQTreeAdapter):
    __select__ = (SEDAIJQTreeAdapter.__select__
                  & is_instance('SEDABinaryDataObject', 'SEDAPhysicalDataObject'))

    def maybe_moved(self):
        return True


class SimplifiedBinaryDataObjectIJQTreeAdapter(SEDAIJQTreeAdapter):
    __select__ = (SEDAIJQTreeAdapter.__select__
                  & is_instance('SEDABinaryDataObject') & simplified_profile())
    rtype_to_archivetransfer = 'seda_binary_data_object'

    def maybe_moved(self):
        return True

    def reparent(self, peid, index):
        archunit = self._cw.entity_from_eid(peid)
        parent = archunit.first_level_choice.content_sequence
        child = self.entity.reverse_seda_data_object_reference_id[0]
        reparent(child, parent.eid, index)
