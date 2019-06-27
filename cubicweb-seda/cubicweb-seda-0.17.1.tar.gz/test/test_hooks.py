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
"""cubicweb-seda unit tests for hooks"""

from os.path import dirname, join
from itertools import chain, repeat

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_compound.entities import copy_entity
from cubicweb_seda import testutils, dataimport


class ValidationHooksTC(CubicWebTC):

    assertValidationError = testutils.assertValidationError

    def test_ref_non_rule_constraints(self):
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity

            access_scheme = create('ConceptScheme', title=u'access')
            access_concept = access_scheme.add_concept(label=u'anyone')
            reuse_scheme = create('ConceptScheme', title=u'reuse')
            reuse_concept = reuse_scheme.add_concept(label=u'share-alike')
            cnx.commit()

            bdo = testutils.create_transfer_to_bdo(cnx)
            transfer = bdo.container[0]
            create('SEDAAccessRuleCodeListVersion',
                   seda_access_rule_code_list_version_from=transfer,
                   seda_access_rule_code_list_version_to=access_scheme)
            create('SEDAReuseRuleCodeListVersion',
                   seda_reuse_rule_code_list_version_from=transfer,
                   seda_reuse_rule_code_list_version_to=reuse_scheme)
            cnx.commit()

            rule_base = create('SEDAAccessRule', seda_access_rule=transfer)
            rule_alt = create('SEDAAltAccessRulePreventInheritance',
                              reverse_seda_alt_access_rule_prevent_inheritance=rule_base)
            non_rule = create('SEDARefNonRuleId', seda_ref_non_rule_id_from=rule_alt)
            cnx.commit()

            with self.assertValidationError(cnx) as cm:
                non_rule.cw_set(seda_ref_non_rule_id_to=reuse_concept)
            self.assertIn('seda_ref_non_rule_id_to-subject', cm.exception.errors)

            non_rule.cw_set(seda_ref_non_rule_id_to=access_concept)
            cnx.commit()

    def test_empty_choice_created(self):
        """Check that a ValidationError is raised when an empty SEDAAlt... entity is created."""
        with self.admin_access.cnx() as cnx:
            # Create an empty SEDAAltAccessRulePreventInheritance
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            access_rule = cnx.create_entity('SEDAAccessRule', seda_access_rule=transfer)
            with self.assertValidationError(cnx) as cm:
                cnx.create_entity('SEDAAltAccessRulePreventInheritance',
                                  reverse_seda_alt_access_rule_prevent_inheritance=access_rule)
            self.assertIn('An alternative cannot be empty',
                          str(cm.exception))

    def test_valid_choice_created(self):
        """Check that everything goes fine when a valid SEDAAlt... entity is created."""
        with self.admin_access.cnx() as cnx:
            # Create an empty SEDAArchiveUnit
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            access_rule = cnx.create_entity('SEDAAccessRule', seda_access_rule=transfer)
            choice = cnx.create_entity('SEDAAltAccessRulePreventInheritance',
                                       reverse_seda_alt_access_rule_prevent_inheritance=access_rule)
            cnx.create_entity('SEDAPreventInheritance', prevent_inheritance=False,
                              seda_prevent_inheritance=choice)
            cnx.commit()

    def test_last_item_in_choice_deleted(self):
        """Check that a ValidationError is raised when the last relation from a SEDAAlt... entity
        is deleted.
        """
        with self.admin_access.cnx() as cnx:
            # Create a valid SEDAAltAccessRulePreventInheritance
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            access_rule = cnx.create_entity('SEDAAccessRule', seda_access_rule=transfer)
            choice = cnx.create_entity('SEDAAltAccessRulePreventInheritance',
                                       reverse_seda_alt_access_rule_prevent_inheritance=access_rule)
            rel = cnx.create_entity('SEDAPreventInheritance', prevent_inheritance=False,
                                    seda_prevent_inheritance=choice)
            cnx.commit()
            # Delete SEDAPreventInheritance
            with self.assertValidationError(cnx) as cm:
                cnx.execute('DELETE SEDAPreventInheritance X WHERE X eid %(rel_eid)s',
                            {'rel_eid': rel.eid})
            self.assertIn('An alternative cannot be empty',
                          str(cm.exception))

    def test_item_in_choice_deleted_with_remaining_item(self):
        """Check that everything goes fine when the a relation from a SEDAAlt... entity
        is deleted but another relation remains.
        """
        with self.admin_access.cnx() as cnx:
            # Create a valid SEDAAltAccessRulePreventInheritance with two items
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            access_rule = cnx.create_entity('SEDAAccessRule', seda_access_rule=transfer)
            choice = cnx.create_entity('SEDAAltAccessRulePreventInheritance',
                                       reverse_seda_alt_access_rule_prevent_inheritance=access_rule)
            rel = cnx.create_entity('SEDAPreventInheritance', prevent_inheritance=False,
                                    seda_prevent_inheritance=choice)
            cnx.create_entity('SEDARefNonRuleId', seda_ref_non_rule_id_from=choice)
            cnx.commit()
            # Delete SEDAPreventInheritance
            cnx.execute('DELETE SEDAPreventInheritance X WHERE X eid %(rel_eid)s',
                        {'rel_eid': rel.eid})
            cnx.commit()


class SetDefaultHooksTC(CubicWebTC):

    def test_default_code_list_version(self):
        with self.admin_access.cnx() as cnx:
            for rtype, etype in chain(zip(('file_category', 'seda_encoding_to'),
                                          repeat(None)),
                                      [('seda_algorithm', 'SEDABinaryDataObject'),
                                       ('seda_rule', 'SEDASeqAppraisalRuleRule'),
                                       ('seda_rule', 'SEDASeqAccessRuleRule'),
                                       ('seda_rule', 'SEDASeqDisseminationRuleRule')]):
                testutils.scheme_for_type(cnx, rtype, etype)
            cnx.commit()
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            cnx.commit()

            self.assertTrue(transfer.reverse_seda_file_format_code_list_version_from)
            self.assertTrue(transfer.reverse_seda_message_digest_algorithm_code_list_version_from)
            self.assertTrue(transfer.reverse_seda_mime_type_code_list_version_from)
            self.assertTrue(transfer.reverse_seda_encoding_code_list_version_from)
            self.assertTrue(transfer.reverse_seda_access_rule_code_list_version_from)
            self.assertTrue(transfer.reverse_seda_appraisal_rule_code_list_version_from)
            self.assertTrue(transfer.reverse_seda_dissemination_rule_code_list_version_from)

    def test_default_card_on_typed_data_object_ref(self):
        """When creating a SEDADataObjectReference in the context of a reference, its cardinality
        should always be 1 (by default any card is allowed since in may be used in the context of
        'main' reference).
        """
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            version_of = cnx.create_entity('SEDAIsVersionOf', seda_is_version_of=unit_alt_seq)
            alt2 = cnx.create_entity('SEDAAltIsVersionOfArchiveUnitRefId',
                                     reverse_seda_alt_is_version_of_archive_unit_ref_id=version_of)
            do_ref = cnx.create_entity('SEDADataObjectReference', seda_data_object_reference=alt2)
            cnx.commit()

            self.assertEqual(do_ref.user_cardinality, '1')

    def test_simplified_profile_do_ref_sync(self):
        """When creating a SEDABinaryDataObject in a simplified profile from the ui, one only
        specifies user_cardinality for it, not for it's associated reference whose cardinality
        should have the same value.
        """
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile',
                                         simplified_profile=True)
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            bdo = testutils.create_data_object(unit_alt_seq, user_cardinality=u'1',
                                               seda_binary_data_object=transfer)
            cnx.commit()
            ref = cnx.find('SEDADataObjectReference').one()

            ref.cw_clear_all_caches()
            self.assertEqual(ref.user_cardinality, '1')

            bdo.cw_set(user_cardinality=u'1..n')
            cnx.commit()
            ref.cw_clear_all_caches()
            self.assertEqual(ref.user_cardinality, '1..n')


class CheckProfileTC(CubicWebTC):

    assertValidationError = testutils.assertValidationError

    def test_base(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'diagnosis testing')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            access_rule = cnx.create_entity('SEDAAccessRule', seda_access_rule=unit_alt_seq)
            cnx.commit()

            with self.assertValidationError(cnx):
                transfer.cw_set(simplified_profile=True)

            access_rule_seq = cnx.create_entity('SEDASeqAccessRuleRule',
                                                reverse_seda_seq_access_rule_rule=access_rule)
            start_date = cnx.create_entity('SEDAStartDate',
                                           seda_start_date=access_rule_seq)
            transfer.cw_set(simplified_profile=True)
            cnx.commit()

            with self.assertValidationError(cnx):
                start_date.cw_set(user_cardinality=u'0..1')

            with self.assertValidationError(cnx):
                access_rule_seq.cw_delete()


class DispatchFileCategoryTC(CubicWebTC):
    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            dataimport.import_seda_schemes(cnx, lcsv_files=[
                (u'Categories de fichier',
                 'file_category', (),
                 join(dirname(__file__), 'data', 'file_categories.csv'))])
            self.categories = dict(cnx.execute(
                'Any LL, C WHERE L label_of C, L label LL, '
                'C in_scheme CS, CS title "Categories de fichier"'))
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile',
                                         simplified_profile=True)
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            bdo = testutils.create_data_object(unit_alt_seq,
                                               seda_binary_data_object=transfer)
            cnx.commit()

        self.transfer_eid = transfer.eid
        self.unit_alt_seq_eid = unit_alt_seq.eid
        self.bdo_eid = bdo.eid

    def test_base(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.entity_from_eid(self.transfer_eid)
            unit_alt_seq = cnx.entity_from_eid(self.unit_alt_seq_eid)
            bdo = cnx.entity_from_eid(self.bdo_eid)

            bdo.cw_set(file_category=self.categories['document'])
            cnx.commit()
            self.assertFormatEqual(bdo,
                                   ['application/msword', 'application/pdf'],
                                   ['fmt/37', 'fmt/38', 'fmt/14'])

            bdo.cw_set(file_category=None)
            cnx.commit()
            self.assertFormatEqual(bdo, [], [])

            bdo.cw_set(file_category=self.categories['doc'])
            cnx.commit()
            self.assertFormatEqual(bdo,
                                   ['application/msword'],
                                   ['fmt/37', 'fmt/38'])

            # test no dispatch occurs on component archive unit...
            unit_comp, unit_comp_alt, unit_comp_alt_seq = testutils.create_archive_unit(
                None, cnx=cnx)
            bdo_comp = testutils.create_data_object(unit_comp_alt_seq)
            cnx.commit()

            bdo_comp.cw_set(file_category=self.categories['document'])
            cnx.commit()
            self.assertFormatEqual(bdo_comp, [], [])
            # until it's imported into some parent
            copy_entity(unit_comp, seda_archive_unit=unit_alt_seq, clone_of=unit_comp)
            cnx.commit()
            imported_bdo, = [x for x in transfer.binary_data_objects if x.eid != bdo.eid]
            self.assertFormatEqual(imported_bdo,
                                   ['application/msword', 'application/pdf'],
                                   ['fmt/37', 'fmt/38', 'fmt/14'])

            # ensure deleting the data object doesn't raise an exception because
            # of erroneous hook
            bdo.cw_delete()
            cnx.commit()

    def test_join(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.entity_from_eid(self.transfer_eid)
            bdo = cnx.entity_from_eid(self.bdo_eid)

            formats = testutils.scheme_for_type(cnx, 'seda_format_id_to', None,
                                                u'fmt/37', u'fmt/14')
            mime_types = testutils.scheme_for_type(cnx, 'seda_mime_type_to', None,
                                                   u'application/msword', u'application/pdf')
            transfer.reverse_seda_file_format_code_list_version_from[0].cw_set(
                seda_file_format_code_list_version_to=formats)
            transfer.reverse_seda_mime_type_code_list_version_from[0].cw_set(
                seda_mime_type_code_list_version_to=mime_types)
            cnx.commit()

            bdo.cw_set(file_category=self.categories['document'])
            cnx.commit()
            self.assertFormatEqual(bdo,
                                   ['application/msword', 'application/pdf'],
                                   ['fmt/37', 'fmt/14'])

    def assertFormatEqual(self, bdo, expected_mime_types, expected_format_ids):
        bdo.cw_clear_all_caches()
        bdo.reverse_seda_mime_type_from[0].cw_clear_all_caches()
        bdo.reverse_seda_format_id_from[0].cw_clear_all_caches()
        mime_types = set(x.label() for x in bdo.reverse_seda_mime_type_from[0].seda_mime_type_to)
        self.assertEqual(mime_types, set(expected_mime_types))
        format_ids = set(x.label() for x in bdo.reverse_seda_format_id_from[0].seda_format_id_to)
        self.assertEqual(format_ids, set(expected_format_ids))


class OrderingHooksTC(CubicWebTC):

    def test_first_level_archive_units(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            unit1 = testutils.create_archive_unit(transfer)[0]
            unit2 = testutils.create_archive_unit(transfer)[0]
            cnx.commit()

            self.assertEqual(unit1.ordering, 1)
            self.assertEqual(unit2.ordering, 2)

    def test_archive_units(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            unit1 = testutils.create_archive_unit(unit_alt_seq)[0]
            unit2 = testutils.create_archive_unit(unit_alt_seq)[0]
            cnx.commit()

            self.assertEqual(unit1.ordering, 1)
            self.assertEqual(unit2.ordering, 2)

    def test_data_objects(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile',
                                         simplified_profile=True)
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            bdo1 = testutils.create_data_object(unit_alt_seq, user_cardinality=u'1',
                                                seda_binary_data_object=transfer)
            bdo2 = testutils.create_data_object(unit_alt_seq, user_cardinality=u'1',
                                                seda_binary_data_object=transfer)
            cnx.commit()

            self.assertEqual(bdo1.ordering, 1)
            self.assertEqual(bdo2.ordering, 2)
            self.assertEqual(bdo1.reverse_seda_data_object_reference_id[0].ordering, 1)
            self.assertEqual(bdo2.reverse_seda_data_object_reference_id[0].ordering, 2)

    def test_remove_keep_in_sync(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            bdo1 = testutils.create_data_object(transfer)
            bdo2 = testutils.create_data_object(transfer)
            cnx.commit()

            bdo1.cw_delete()
            cnx.commit()

            bdo2.cw_clear_all_caches()
            self.assertEqual(bdo2.ordering, 1)


if __name__ == '__main__':
    import unittest
    unittest.main()
