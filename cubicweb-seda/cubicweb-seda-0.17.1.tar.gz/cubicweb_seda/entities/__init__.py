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
"""Custom logic (eg entities and adapters) for cubicweb-seda."""

import json

from logilab.common.registry import objectify_predicate

from cubicweb.predicates import is_instance
from cubicweb.view import EntityAdapter
from cubicweb_compound.entities import IContainer, IContained, IClonableAdapter

from .. import seda_profile_container_def
from ..xsd import XSDMMapping
from ..xsd2yams import RULE_TYPES


XSDM_MAPPING = XSDMMapping('ArchiveTransfer')


def parent_and_container(entity):
    """Attempt to return the direct parent and container from the entity, handling case where entity
    is being created and container information will be found through linkto or parent form
    (partially supported)
    """
    if entity.has_eid():
        # entity is expected to be a contained entity, not the container itself
        container = entity.cw_adapt_to('IContained').container
        parent = entity.cw_adapt_to('IContained').parent
        if container is None:
            # entity may be both container and contained, and in this case is a container
            if entity.cw_adapt_to('IContainer') is None:
                entity.debug('cannot adapt %s as IContainer in parent_and_container()',
                             entity)
                return None, None
            container = entity
    else:
        req = entity._cw
        # but parent entity, retrieved through linkto, may be the container itself or a
        # contained entity
        try:
            parent_eid = int(req.form['__linkto'].split(':')[1])
        except KeyError:
            # ajax created form
            try:
                parent_eid = int(json.loads(req.form['arg'][0]))
            except (KeyError, ValueError):
                if 'sedaContainerEID' in req.form:
                    container = req.entity_from_eid(int(req.form['sedaContainerEID']))
                    return None, container
                if 'referenced_by' in req.form:
                    entity = req.entity_from_eid(int(req.form['referenced_by']))
                    container = entity.cw_adapt_to('IContained').container
                    return None, container
                # unable to get parent eid for now :(
                return None, None
        parent = req.entity_from_eid(parent_eid)
        # handle IContained first: in case entity support both interface we want to go to the
        # uppermost parent
        icontained = parent.cw_adapt_to('IContained')
        if icontained is not None and icontained.container:
            container = icontained.container
        elif parent.cw_adapt_to('IContainer'):
            container = parent
    return parent, container


def _seda_container_from_context(rset, entity, **kwargs):
    if entity is None:
        if 'row' in kwargs:
            entity = rset.get_entity(kwargs['row'], kwargs.get('col', 0))
        elif len(rset) == 1:
            entity = rset.one()
        else:
            return None
    # protect against unrelated entity types
    if not entity.cw_etype.startswith('SEDA'):
        return None
    if entity.cw_etype != 'SEDAArchiveTransfer':
        entity = parent_and_container(entity)[1]
    return entity


@objectify_predicate
def component_unit(cls, req, rset=None, entity=None, **kwargs):
    """Predicate returning 1 score if context entity is within "component" archive unit (i.e.
    container root is not a SEDAArchiveTransfer but a SEDAArchiveUnit).
    """
    entity = _seda_container_from_context(rset, entity, **kwargs)
    if entity and entity.cw_etype == 'SEDAArchiveUnit':
        return 1
    return 0


@objectify_predicate
def simplified_profile(cls, req, rset=None, entity=None, **kwargs):
    """Predicate returning 1 score if context entity is within a simplified profile."""
    container = _seda_container_from_context(rset, entity, **kwargs)
    if container is None:
        # Detect creation of a component archive unit, which are supposed to be
        # simplified. If we can't get a container and we're creating an archive
        # unit, it must be an archive unit component (else it's parent container
        # should have been retrieved)
        if getattr(req, 'form', {}).get('etype') == 'SEDAArchiveUnit':
            return 1
        return 0
    if container.cw_etype == 'SEDAArchiveUnit':
        # XXX archive unit component, for now suppose it's "simplified"
        return 1
    return 1 if container.simplified_profile else 0


def is_full_seda2_profile(entity=None, rset=None, **kwargs):
    """Return 1 if context entity is within a full seda2 profile, else 0."""
    entity = _seda_container_from_context(rset, entity, **kwargs)
    if entity is None:
        return 1
    if entity.cw_etype == 'SEDAArchiveUnit':
        # XXX archive unit component, for now suppose it's "simplified"
        return 0
    return 0 if entity.simplified_profile else 1


@objectify_predicate
def full_seda2_profile(cls, req, rset=None, entity=None, **kwargs):
    """Predicate returning 1 score if context entity is within a full seda2 profile."""
    return is_full_seda2_profile(entity, rset, **kwargs)


def rule_type_from_etype(etype):
    """Return the rule type (e.g. 'access') from an etype enclosing the information
    (e.g. 'SEDAAltAccessRulePreventInheritance', 'SEDASeqAaccessRuleRule' or 'SEDAAccessRule')
    """
    if etype.startswith('SEDAAlt'):
        rule_type = etype[len('SEDAAlt'):-len('RulePreventInheritance')]
    elif etype.startswith('SEDASeq'):
        rule_type = etype[len('SEDASeq'):-len('RuleRule')]
    else:
        rule_type = etype[len('SEDA'):-len('Rule')]
    rule_type = rule_type.lower()
    assert rule_type in RULE_TYPES, 'unhandled etype {0}'.format(etype)
    return rule_type


class DirectLinkIContained(IContained):
    """IContained implementation using a relation that link every contained entities to its parent
    container.
    """
    __abstract__ = True

    @property
    def container(self):
        """Return the container to which this entity belongs, or None."""
        container = self.entity.related('container', entities=True)
        return container and container[0] or None


class SEDAArchiveTransferIClonableAdapter(IClonableAdapter):
    """Cloning adapter for SEDA profiles."""
    __select__ = is_instance('SEDAArchiveTransfer')
    rtype = 'clone_of'
    skiprtypes = ('container',)
    # this relation isn't composite but it should be followed for cloning since
    # it's an intra-container relation
    follow_relations = [('seda_data_object_reference_id', 'subject')]


class SEDAArchiveUnitIClonableAdapter(SEDAArchiveTransferIClonableAdapter):
    """Cloning adapter for SEDA components."""
    __select__ = is_instance('SEDAArchiveUnit')

    def clone_into(self, clone):
        """Recursivily clone the container graph of this entity into `clone`."""
        if clone.seda_archive_unit and (
                clone.seda_archive_unit[0].cw_etype == 'SEDAArchiveTransfer'
                or clone.seda_archive_unit[0].container[0].cw_etype == 'SEDAArchiveTransfer'):
            # clone is parented to a transfer profile, we need to properly handle binary/physical
            # data objects
            data_objects = self._cw.execute(
                'Any X WHERE X is IN (SEDABinaryDataObject, SEDAPhysicalDataObject),'
                ' X container %(c)s', {'c': self.entity.eid})
        else:
            data_objects = None
        clones = super(SEDAArchiveUnitIClonableAdapter, self).clone_into(clone)
        if data_objects is not None:
            if clone.seda_archive_unit[0].cw_etype == 'SEDAArchiveTransfer':
                transfer = clone.seda_archive_unit[0]
            else:
                transfer = clone.seda_archive_unit[0].container[0]
            for data_object in data_objects.entities():
                rtype = {
                    'SEDABinaryDataObject': 'seda_binary_data_object',
                    'SEDAPhysicalDataObject': 'seda_physical_data_object',
                }[data_object.cw_etype]
                clones[data_object].cw_set(**{rtype: transfer})


class XmlIdAdapter(EntityAdapter):
    """Adapter for entity to be inserted in XML document and for which an
    xml:id attribute needs to be generated.
    """
    __regid__ = 'IXmlId'
    __select__ = is_instance('Any')

    def id(self):
        return u'id{}'.format(self.entity.eid)


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    vreg.register(IContainer.build_class('SEDAArchiveTransfer'))
    vreg.register(IContainer.build_class('SEDAArchiveUnit'))  # archive unit may also be a container
    for etype, parent_relations in sorted(seda_profile_container_def(vreg.schema)):
        cls = DirectLinkIContained.build_class(etype, parent_relations)
        assert cls
        vreg.register(cls)
        if etype in ('SEDABinaryDataObject', 'SEDAPhysicalDataObject'):
            # insert seda_data_object_reference_id as potential parent,
            # necessary in case of data object in a component archive unit
            cls.parent_relations = list(cls.parent_relations)
            cls.parent_relations.append(('seda_data_object_reference_id', 'object'))
