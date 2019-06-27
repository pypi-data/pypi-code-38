# copyright 2016-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""Miscellaneous test utilities."""

from contextlib import contextmanager

from cubicweb import ValidationError, Unauthorized
from cubicweb.rset import NoResultError


@contextmanager
def assertValidationError(self, cnx):
    with self.assertRaises(ValidationError) as cm:
        yield cm
        cnx.commit()
    cnx.rollback()


@contextmanager
def assertUnauthorized(self, cnx):
    with self.assertRaises(Unauthorized) as cm:
        yield cm
        cnx.commit()
    cnx.rollback()


def create_transfer_to_bdo(cnx):
    """Create minimal ArchiveTransfer down to a BinaryDataObject and return the later."""
    transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
    bdo = create_data_object(transfer)
    # commit and clear cache to allow access to container relation
    cnx.commit()
    bdo.cw_clear_all_caches()
    return bdo


def create_archive_unit(parent, archive_unit_reference=False, title=None, **kwargs):
    """Create an archive unit and its mandatory children:

    return (archive unit, alternative, sequence) if archive_unit_reference is false (the default),
    else (archive unit, alternative, reference).
    """
    cnx = kwargs.pop('cnx', getattr(parent, '_cw', None))
    kwargs.setdefault('user_annotation', u'archive unit title')
    au = cnx.create_entity('SEDAArchiveUnit', seda_archive_unit=parent, **kwargs)
    alt = cnx.create_entity('SEDAAltArchiveUnitArchiveUnitRefId',
                            reverse_seda_alt_archive_unit_archive_unit_ref_id=au)
    if archive_unit_reference:
        last = cnx.create_entity('SEDAArchiveUnitRefId', seda_archive_unit_ref_id_from=alt)
    else:
        try:
            description_level = cnx.execute('Concept C WHERE L label_of C, L label "file"').one()
        except NoResultError:
            with cnx.security_enabled(write=False):
                scheme = scheme_for_type(cnx, 'seda_description_level', None, u'file')
                description_level = scheme.reverse_in_scheme[0]
        last = cnx.create_entity(
            'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement',
            reverse_seda_seq_alt_archive_unit_archive_unit_ref_id_management=alt,
            seda_description_level=description_level)
        cnx.create_entity('SEDATitle', seda_title=last, title=title)

    return au, alt, last


def create_data_object(parent, **kwargs):
    cnx = getattr(parent, '_cw', None)
    if parent.cw_etype == 'SEDAArchiveTransfer':
        kwargs['seda_binary_data_object'] = parent
    kwargs.setdefault('user_annotation', u'data object title')
    bdo = cnx.create_entity('SEDABinaryDataObject', **kwargs)
    choice = cnx.create_entity('SEDAAltBinaryDataObjectAttachment',
                               reverse_seda_alt_binary_data_object_attachment=bdo)
    cnx.create_entity('SEDAAttachment', seda_attachment=choice)  # Choice cannot be empty
    if parent.cw_etype != 'SEDAArchiveTransfer':
        cnx.create_entity('SEDADataObjectReference', user_cardinality=u'0..n',
                          seda_data_object_reference=parent,
                          seda_data_object_reference_id=bdo)

    return bdo


def create_authority_record(cnx, name, kind=u'person', **kwargs):
    """Return an AuthorityRecord with specified kind and name."""
    kind_eid = cnx.find('AgentKind', name=kind)[0][0]
    record = cnx.create_entity('AuthorityRecord', agent_kind=kind_eid, **kwargs)
    cnx.create_entity('NameEntry', parts=name, form_variant=u'authorized',
                      name_entry_for=record)
    return record


def map_cs_to_type(scheme, rtype, etype=None):
    cnx = scheme._cw
    cnx.execute('SET CS scheme_relation_type RT WHERE CS eid %(cs)s, RT name %(rt)s',
                {'cs': scheme.eid, 'rt': rtype})
    if etype is not None:
        cnx.execute('SET CS scheme_entity_type ET WHERE CS eid %(cs)s, ET name %(et)s',
                    {'cs': scheme.eid, 'et': etype})


# extra kwargs useful for client lib (e.g. saem)
def scheme_for_type(cnx, rtype, etype, *concept_labels, **kwargs):
    """Create a concept scheme an map it to give rtype and optional etype."""
    scheme = cnx.create_entity('ConceptScheme', title=u'{0}/{1} vocabulary'.format(rtype, etype),
                               **kwargs)
    map_cs_to_type(scheme, rtype, etype)
    for label in concept_labels:
        scheme.add_concept(label)
    return scheme


def scheme_for_rtype(cnx, rtype, *concept_labels):
    return scheme_for_type(cnx, rtype, None, *concept_labels)
