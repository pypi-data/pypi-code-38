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
"""cubicweb-seda unit tests for entities.container"""

import json
import unittest

from six import text_type

from logilab.common import attrdict

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_seda.entities import (seda_profile_container_def, simplified_profile,
                                    full_seda2_profile, parent_and_container,
                                    rule_type_from_etype, custom, itree)

from cubicweb_seda.testutils import create_archive_unit, create_data_object


def sort_container(container_def):
    for k, v in container_def:
        yield k, sorted(v)


class ContainerTC(CubicWebTC):

    def test_seda_profile_container(self):
        # line below should be copied from entities.container.registration_callback
        container_def = seda_profile_container_def(self.schema)
        container_def = dict(sort_container(container_def))
        self.assertEqual(container_def['SEDAMimeType'],
                         [('seda_mime_type_from', 'subject')])
        self.assertNotIn('ConceptScheme', container_def)
        self.assertNotIn('Concept', container_def)
        self.assertNotIn('AuthorityRecord', container_def)
        entity = self.vreg['etypes'].etype_class('SEDAArchiveTransfer')(self)
        self.assertIsNotNone(entity.cw_adapt_to('IContainer'))
        self.assertIsNone(entity.cw_adapt_to('IContained'))

    def test_container_relation(self):
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity
            transfer = create('SEDAArchiveTransfer', title=u'test profile')
            mtclv = create('SEDAMimeTypeCodeListVersion',
                           seda_mime_type_code_list_version_from=transfer)
            access_rule = create('SEDAAccessRule', seda_access_rule=transfer)
            cnx.commit()
            for entity in (mtclv, access_rule):
                entity.cw_clear_all_caches()
                self.assertEqual(entity.cw_adapt_to('IContained').container.eid, transfer.eid)
            access_rule_seq = create('SEDASeqAccessRuleRule',
                                     reverse_seda_seq_access_rule_rule=access_rule)
            start_date = create('SEDAStartDate', seda_start_date=access_rule_seq)
            cnx.commit()
            for entity in (access_rule_seq, start_date):
                entity.cw_clear_all_caches()
                self.assertEqual(entity.cw_adapt_to('IContained').container.eid, transfer.eid)

    def test_container_relation_archive_unit(self):
        """Ensure that container relation is deleted upon deletion on
        "seda_archive_unit" relation.
        """
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test')
            unit, _, _ = create_archive_unit(transfer, cnx=cnx,
                                             user_cardinality=u'1',
                                             user_annotation=u'plop')
            cnx.commit()
            unit.cw_clear_all_caches()
            self.assertEqual(unit.container, (transfer, ))
            self.assertIn(unit, transfer.reverse_seda_archive_unit)
            transfer.cw_set(reverse_seda_archive_unit=None)
            cnx.commit()
            unit.cw_clear_all_caches()
            self.assertEqual(unit.container, ())

    def test_archive_unit_container_clone(self):
        """Functional test for SEDA component clone."""
        with self.admin_access.cnx() as cnx:
            unit, unit_alt, unit_alt_seq = create_archive_unit(None, cnx=cnx)
            bdo = create_data_object(unit_alt_seq)
            cnx.commit()

            unit.cw_clear_all_caches()
            self.assertEqual(unit.container, ())  # XXX arguable
            unit_alt_seq.cw_clear_all_caches()
            self.assertEqual(unit_alt_seq.container[0].eid, unit.eid)
            bdo.cw_clear_all_caches()
            self.assertEqual(bdo.container[0].eid, unit.eid)

            # test clone without reparenting
            cloned = cnx.create_entity(unit.cw_etype, user_annotation=u'clone',
                                       clone_of=unit)
            cnx.commit()
            cloned.cw_clear_all_caches()
            self.assertEqual(cloned.user_annotation, 'clone')
            cloned_unit_alt_seq = cloned.first_level_choice.content_sequence
            self.assertEqual(cloned_unit_alt_seq.container[0].eid, cloned.eid)
            cloned_bdo = (cloned_unit_alt_seq.reverse_seda_data_object_reference[0]
                          .seda_data_object_reference_id[0])
            self.assertEqual(cloned_bdo.container[0].eid, cloned.eid)

            # test clone with reparenting
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            cloned = cnx.create_entity(unit.cw_etype,
                                       user_annotation=u'I am mandatory',
                                       clone_of=unit,
                                       seda_archive_unit=transfer)
            cnx.commit()
            cloned.cw_clear_all_caches()
            self.assertEqual(cloned.container[0].eid, transfer.eid)
            cloned.cw_clear_all_caches()
            cloned_unit_alt_seq = cloned.first_level_choice.content_sequence
            self.assertEqual(cloned_unit_alt_seq.container[0].eid, transfer.eid)
            cloned_bdo = (cloned_unit_alt_seq.reverse_seda_data_object_reference[0]
                          .seda_data_object_reference_id[0])
            self.assertEqual(cloned_bdo.container[0].eid, transfer.eid)
            cloned_bdo.cw_clear_all_caches()
            self.assertEqual(cloned_bdo.seda_binary_data_object[0].eid, transfer.eid)

    def test_archive_transfer_clone(self):
        """Functional test for SEDA profile cloning."""
        with self.admin_access.cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'Algorithms')
            concept = scheme.add_concept(u'md5')
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            cnx.create_entity('SEDAMessageDigestAlgorithmCodeListVersion',
                              seda_message_digest_algorithm_code_list_version_from=transfer,
                              seda_message_digest_algorithm_code_list_version_to=scheme)
            unit, unit_alt, unit_alt_seq = create_archive_unit(
                transfer, cnx=cnx, title=u'hello')
            create_data_object(transfer, seda_algorithm=concept)
            cnx.commit()

            clone = cnx.create_entity('SEDAArchiveTransfer', title=u'Clone', clone_of=transfer)
            cnx.commit()

            self.assertEqual((clone.reverse_seda_message_digest_algorithm_code_list_version_from[0].
                             seda_message_digest_algorithm_code_list_version_to[0].eid),
                             scheme.eid)
            seq = clone.archive_units[0].first_level_choice.content_sequence
            self.assertEqual(seq.title.title, 'hello')
            self.assertEqual(transfer.binary_data_objects[0].seda_algorithm[0].eid, concept.eid)

    def test_container_clone_clone(self):
        """Functional test for SEDA component clone."""
        with self.admin_access.cnx() as cnx:
            unit, unit_alt, unit_alt_seq = create_archive_unit(None, cnx=cnx)
            cnx.commit()

            cloned = cnx.create_entity(unit.cw_etype, user_annotation=u'x', clone_of=unit)
            cnx.commit()
            cloned.cw_clear_all_caches()

            cloned2 = cnx.create_entity(unit.cw_etype, user_annotation=u'Y')
            # mimick what's occurs when you're using the copy form
            cloned2.copy_relations(cloned.eid)  # 1. copy relation
            self.assertFalse(cloned2.clone_of)
            cloned2.cw_set(clone_of=cloned.eid)  # 2. execute __linkto (which trigger cloning)

            cnx.commit()

            cloned2.cw_clear_all_caches()
            self.assertEqual(len(cloned2.seda_alt_archive_unit_archive_unit_ref_id), 1)

            unit_alt.cw_clear_all_caches()
            self.assertEqual(unit_alt.container[0].eid, unit.eid)
            self.assertEqual(cloned.seda_alt_archive_unit_archive_unit_ref_id[0].container[0].eid,
                             cloned.eid)
            self.assertEqual(cloned2.seda_alt_archive_unit_archive_unit_ref_id[0].container[0].eid,
                             cloned2.eid)

    def test_data_object_reference_clone(self):
        with self.admin_access.repo_cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            unit, unit_alt, unit_alt_seq = create_archive_unit(transfer)
            # don't add link from data object to transfer intentionally to force
            # going through the archive unit to clone it
            bdo = create_data_object(unit_alt_seq)
            cnx.commit()

            clone = cnx.create_entity('SEDAArchiveTransfer', title=u'Clone',
                                      clone_of=transfer)
            cnx.commit()

            # Ensure data object is cloned through data_object_reference_id and
            # container relation is properly handled
            bdo_clone = cnx.execute('Any MAX(X) WHERE X is SEDABinaryDataObject').one()
            self.assertNotEqual(bdo_clone.eid, bdo.eid)
            bdo.cw_clear_all_caches()
            self.assertEqual([e.eid for e in bdo.container], [transfer.eid])
            self.assertEqual([e.eid for e in bdo_clone.container], [clone.eid])

            self.failIf(cnx.execute('Any X GROUPBY X WHERE X container C HAVING COUNT(C) > 1'))
            self.failIf(cnx.execute('Any X WHERE NOT X container C'))


class FakeEntity(object):
    cw_etype = 'Whatever'

    def __init__(self, _cw):
        self._cw = _cw

    def has_eid(self):
        return False


class PredicatesTC(CubicWebTC):

    def test_simplified_profile(self):
        simplified_profile_pred = simplified_profile()
        full_seda2_profile_pred = full_seda2_profile()
        with self.admin_access.web_request() as req:
            transfer = req.create_entity('SEDAArchiveTransfer', title=u'test profile')
            self.assertEqual(simplified_profile_pred(None, req, entity=transfer), 0)
            self.assertEqual(full_seda2_profile_pred(None, req, entity=transfer), 1)
            self.assertEqual(simplified_profile_pred(None, req, rset=transfer.as_rset()), 0)
            self.assertEqual(full_seda2_profile_pred(None, req, rset=transfer.as_rset()), 1)
            access_rule = req.create_entity('SEDAAccessRule', seda_access_rule=transfer)
            req.cnx.commit()  # needed to set the container relation
            self.assertEqual(simplified_profile_pred(None, req, entity=access_rule), 0)
            self.assertEqual(full_seda2_profile_pred(None, req, entity=access_rule), 1)
            req.form['__linkto'] = 'whatever:%s:whatever' % transfer.eid
            being_created = FakeEntity(req)
            self.assertEqual(simplified_profile_pred(None, req, entity=being_created), 0)
            self.assertEqual(full_seda2_profile_pred(None, req, entity=being_created), 1)
            del req.form['__linkto']
            req.form['arg'] = [text_type(transfer.eid)]
            self.assertEqual(simplified_profile_pred(None, req, entity=being_created), 0)
            self.assertEqual(full_seda2_profile_pred(None, req, entity=being_created), 1)
            transfer.cw_set(simplified_profile=True)
            self.assertEqual(simplified_profile_pred(None, req, entity=transfer), 1)
            self.assertEqual(full_seda2_profile_pred(None, req, entity=transfer), 0)

            req.form = {'etype': 'SEDAArchiveUnit'}
            etype_vreg = req.vreg['etypes']
            unit = etype_vreg.etype_class('SEDAArchiveUnit')(req)
            self.assertEqual(simplified_profile_pred(None, req, entity=unit), 1)
            entity = etype_vreg.etype_class('SEDASeqAltArchiveUnitArchiveUnitRefIdManagement')(req)
            self.assertEqual(simplified_profile_pred(None, req, entity=entity), 1)


class ITreeTC(CubicWebTC):

    def assertChildren(self, entity, expected_eids):
        entity.cw_clear_all_caches()
        itree = entity.cw_adapt_to('ITreeBase')
        children = [x.eid for x in itree.iterchildren()]
        self.assertEqual(children, expected_eids)

    def assertParent(self, entity, expected_eid):
        entity.cw_clear_all_caches()
        itree = entity.cw_adapt_to('ITreeBase')
        parent = itree.parent()
        if parent:
            parent_eid = parent.eid
        else:
            parent_eid = None
        self.assertEqual(parent_eid, expected_eid)

    def test(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            au, alt, seq = create_archive_unit(transfer)
            au2 = create_archive_unit(transfer)[0]
            do_ref = cnx.create_entity('SEDADataObjectReference',
                                       seda_data_object_reference=seq)
            bdo = create_data_object(transfer,
                                     reverse_seda_data_object_reference_id=do_ref)
            do_ref2 = cnx.create_entity('SEDADataObjectReference',
                                        seda_data_object_reference=seq)
            bdo2 = create_data_object(transfer,
                                      reverse_seda_data_object_reference_id=do_ref2)
            cnx.commit()

            self.assertChildren(transfer, [bdo.eid, bdo2.eid, au.eid, au2.eid])
            self.assertChildren(au, [])
            self.assertParent(transfer, None)
            self.assertParent(au, transfer.eid)
            self.assertParent(bdo, transfer.eid)

            transfer.cw_set(simplified_profile=True)
            cnx.commit()

            self.assertChildren(transfer, [au.eid, au2.eid])
            self.assertChildren(au, [bdo.eid, bdo2.eid])
            self.assertParent(transfer, None)
            self.assertParent(au, transfer.eid)
            self.assertParent(bdo, au.eid)

            au.cw_set(ordering=2)
            au2.cw_set(ordering=1)
            bdo.cw_set(ordering=2)
            bdo2.cw_set(ordering=1)
            do_ref.cw_set(ordering=2)
            do_ref2.cw_set(ordering=1)
            cnx.commit()

            self.assertChildren(transfer, [au2.eid, au.eid])
            self.assertChildren(au, [bdo2.eid, bdo.eid])

            transfer.cw_set(simplified_profile=False)
            cnx.commit()

            self.assertChildren(transfer, [bdo2.eid, bdo.eid, au2.eid, au.eid])


class ReorderTC(CubicWebTC):

    def test_reorder_base(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'Test')
            bdo1 = create_data_object(transfer)
            bdo2 = create_data_object(transfer)
            bdo3 = create_data_object(transfer)
            cnx.commit()

            itree.move_child_at_index(cnx, transfer.eid, bdo3.eid, 0)
            transfer.cw_clear_all_caches()
            self.assertEqual([(x.eid, x.ordering)
                              for x in transfer.cw_adapt_to('ITreeBase').iterchildren()],
                             [(bdo3.eid, 1), (bdo1.eid, 2), (bdo2.eid, 3)])

            itree.move_child_at_index(cnx, transfer.eid, bdo3.eid, 3)
            transfer.cw_clear_all_caches()
            self.assertEqual([(x.eid, x.ordering)
                              for x in transfer.cw_adapt_to('ITreeBase').iterchildren()],
                             [(bdo1.eid, 1), (bdo2.eid, 2), (bdo3.eid, 3)])

            itree.move_child_at_index(cnx, transfer.eid, bdo1.eid, 2)
            transfer.cw_clear_all_caches()
            self.assertEqual([(x.eid, x.ordering)
                              for x in transfer.cw_adapt_to('ITreeBase').iterchildren()],
                             [(bdo2.eid, 1), (bdo1.eid, 2), (bdo3.eid, 3)])

            itree.move_child_at_index(cnx, transfer.eid, bdo3.eid, 1)
            transfer.cw_clear_all_caches()
            self.assertEqual([(x.eid, x.ordering)
                              for x in transfer.cw_adapt_to('ITreeBase').iterchildren()],
                             [(bdo2.eid, 1), (bdo3.eid, 2), (bdo1.eid, 3)])


class RuleFromETypeTC(unittest.TestCase):
    def test_rule_from_etype(self):
        for rule_type in ('access', 'appraisal', 'classification',
                          'reuse', 'dissemination', 'storage'):
            for prefix, suffix in [
                    ('SEDAAlt', 'RulePreventInheritance'),
                    ('SEDASeq', 'RuleRule'),
                    ('SEDA', 'Rule'),
            ]:
                self.assertEqual(rule_type_from_etype(prefix + rule_type.capitalize() + suffix),
                                 rule_type)


class ParentAndContainerTC(CubicWebTC):

    def test_nodata(self):
        with self.admin_access.web_request() as req:
            parent, container = parent_and_container(attrdict(_cw=req, has_eid=lambda: False))
            self.assertIsNone(parent)
            self.assertIsNone(container)

    def test_linkto(self):
        with self.admin_access.web_request() as req:
            transfer = req.cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            req.form['__linkto'] = 'x:{0}:y'.format(transfer.eid)
            parent, container = parent_and_container(attrdict(_cw=req, has_eid=lambda: False))
            self.assertEqual(parent.eid, transfer.eid)
            self.assertEqual(container.eid, transfer.eid)

    def test_arg(self):
        with self.admin_access.web_request() as req:
            transfer = req.cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            req.form['arg'] = [json.dumps(transfer.eid)]
            parent, container = parent_and_container(attrdict(_cw=req, has_eid=lambda: False))
            self.assertEqual(parent.eid, transfer.eid)
            self.assertEqual(container.eid, transfer.eid)

    def test_eid(self):
        with self.admin_access.web_request() as req:
            transfer = req.cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            req.form['sedaContainerEID'] = text_type(transfer.eid)
            parent, container = parent_and_container(attrdict(_cw=req, has_eid=lambda: False))
            self.assertIsNone(parent)
            self.assertEqual(container.eid, transfer.eid)


class CustomEntitiesTC(CubicWebTC):

    def test_title(self):
        with self.admin_access.cnx() as cnx:
            for etype in ('SEDAArchiveUnit', 'SEDABinaryDataObject', 'SEDAPhysicalDataObject'):
                ent = cnx.create_entity(etype, user_annotation=u'bla bla\nbli bli blo\n')
                self.assertEqual(ent.dc_title(), u'bla bla')

    def test_climb_rule_holders(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            unit, _, unit_alt_seq = create_archive_unit(transfer)
            subunit, _, subunit_alt_seq = create_archive_unit(unit_alt_seq)
            cnx.commit()

            self.assertEqual(list(custom._climb_rule_holders(subunit_alt_seq)),
                             [subunit_alt_seq, unit_alt_seq, transfer])
            self.assertEqual(list(custom._climb_rule_holders(subunit)),
                             [subunit_alt_seq, unit_alt_seq, transfer])
            self.assertEqual(list(custom._climb_rule_holders(unit_alt_seq)),
                             [unit_alt_seq, transfer])
            self.assertEqual(list(custom._climb_rule_holders(unit)),
                             [unit_alt_seq, transfer])
            self.assertEqual(list(custom._climb_rule_holders(transfer)),
                             [transfer])


if __name__ == '__main__':
    unittest.main()
