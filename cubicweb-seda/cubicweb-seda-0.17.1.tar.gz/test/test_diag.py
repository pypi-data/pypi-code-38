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
"""cubicweb-seda versions compatibility diagnosis test."""

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_seda import testutils


class CompatAnalyzerTC(CubicWebTC):

    def test_rules(self):
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity

            transfer = create('SEDAArchiveTransfer', title=u'diagnosis testing')
            doctor = transfer.cw_adapt_to('ISEDACompatAnalyzer')
            cnx.commit()
            self.assertFailingRules(doctor, ['SEDA 2.0', 'SEDA 1.0', 'SEDA 0.2', 'simplified'])

            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            transfer.cw_clear_all_caches()
            cnx.commit()
            self.assertFailingRules(doctor, ['SEDA 2.0', 'SEDA 0.2', 'simplified'],
                                    'seda1_need_access_rule')

            access_rule = create('SEDAAccessRule', seda_access_rule=unit_alt_seq)
            unit_alt_seq.cw_clear_all_caches()
            cnx.commit()
            self.assertFailingRules(doctor, ['SEDA 2.0'], 'rule_without_rule')

            access_rule_seq = create('SEDASeqAccessRuleRule',
                                     user_cardinality=u'1..n',
                                     reverse_seda_seq_access_rule_rule=access_rule)
            access_rule.cw_clear_all_caches()
            cnx.commit()
            self.assertFailingRules(doctor, ['SEDA 2.0'],
                                    'rule_unsupported_card', 'rule_need_start_date')

            access_rule_seq.cw_set(user_cardinality=u'1')
            start_date = create('SEDAStartDate',
                                user_cardinality=u'0..1',
                                seda_start_date=access_rule_seq)
            access_rule_seq.cw_clear_all_caches()
            cnx.commit()
            self.assertFailingRules(doctor, ['SEDA 2.0'],
                                    'rule_start_unsupported_card')

            start_date.cw_set(user_cardinality=u'1')
            start_date.cw_clear_all_caches()
            access_rule_seq2 = create('SEDASeqAccessRuleRule',
                                      user_cardinality=u'1..n',
                                      reverse_seda_seq_access_rule_rule=access_rule)
            access_rule.cw_clear_all_caches()
            cnx.commit()
            self.assertFailingRules(doctor, ['SEDA 2.0'],
                                    'rule_with_too_much_rules')

            access_rule_seq2.cw_delete()
            inherit_ctl = create('SEDAAltAccessRulePreventInheritance',
                                 reverse_seda_alt_access_rule_prevent_inheritance=access_rule)
            create('SEDARefNonRuleId', seda_ref_non_rule_id_from=inherit_ctl)
            access_rule.cw_clear_all_caches()
            cnx.commit()
            self.assertFailingRules(doctor, ['SEDA 2.0'],
                                    'rule_ref_non_rule_id')

    def test_custodial_history(self):
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity

            transfer = create('SEDAArchiveTransfer', title=u'diagnosis testing')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            access_rule = create('SEDAAccessRule',
                                 seda_access_rule=unit_alt_seq)
            access_rule_seq = create('SEDASeqAccessRuleRule',
                                     reverse_seda_seq_access_rule_rule=access_rule)
            create('SEDAStartDate',
                   user_cardinality=u'1',
                   seda_start_date=access_rule_seq)

            history_item = create('SEDACustodialHistoryItem',
                                  seda_custodial_history_item=unit_alt_seq)

            doctor = transfer.cw_adapt_to('ISEDACompatAnalyzer')
            cnx.commit()
            self.assertFailingRules(doctor, ['SEDA 2.0', 'SEDA 1.0', 'SEDA 0.2', 'simplified'])

            history_item2 = create('SEDACustodialHistoryItem',
                                   seda_custodial_history_item=unit_alt_seq)
            unit_alt_seq.cw_clear_all_caches()
            cnx.commit()
            self.assertFailingRules(doctor, ['SEDA 2.0', 'SEDA 1.0', 'simplified'],
                                    'seda02_custodial_history_items')

            history_item2.cw_delete()
            create('SEDAwhen', seda_when=history_item)
            unit_alt_seq.cw_clear_all_caches()
            history_item.cw_clear_all_caches()
            cnx.commit()
            self.assertFailingRules(doctor, ['SEDA 2.0', 'SEDA 1.0', 'simplified'],
                                    'seda02_custodial_history_when')

    def test_archive_unit_reference_in_transfer(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'diagnosis testing')
            testutils.create_archive_unit(transfer, archive_unit_reference=True)

            doctor = transfer.cw_adapt_to('ISEDACompatAnalyzer')
            cnx.commit()
            self.assertFailingRules(doctor, ['SEDA 2.0'], 'use_archive_unit_ref')

    def test_archive_unit_reference_in_archive_unit(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'diagnosis testing')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            testutils.create_archive_unit(unit_alt_seq, archive_unit_reference=True)

            doctor = transfer.cw_adapt_to('ISEDACompatAnalyzer')
            cnx.commit()
            self.assertFailingRules(doctor, ['SEDA 2.0'],
                                    'use_archive_unit_ref', 'seda1_need_access_rule')

    def assertFailingRules(self, doctor, expected_formats, *expected_rule_ids):
        doctor.entity.cw_clear_all_caches()
        rule_ids = set(rule_id for rule_id, entity in doctor.failing_rules())
        self.assertEqual(rule_ids, set(expected_rule_ids))
        expected_formats.append('RNG')
        self.assertEqual(doctor.diagnose(), set(expected_formats))
        self.assertEqual(doctor.entity.compat_list, ', '.join(sorted(expected_formats)))

    # in tests below, assertIsRNGAmbiguous is used to test that hooks have
    # properly detected the error (or fix) while assertRNGAmbiguousDiagnostic
    # will test the underlying details of the diagnosis tool.

    def test_multiple_child_unhandled_cardinality_archive_unit(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            doctor = transfer.cw_adapt_to('ISEDACompatAnalyzer')
            testutils.create_archive_unit(transfer)
            unit2 = testutils.create_archive_unit(transfer, user_cardinality=u'0..1')[0]
            testutils.create_archive_unit(transfer, user_cardinality=u'1..n')
            cnx.commit()

            self.assertIsRNGAmbiguous(transfer, True)
            self.assertErrorOn(doctor, 'rng_ambiguity', [(transfer, 'seda_archive_units_tab')])

            unit2.cw_set(user_cardinality=u'1')
            cnx.commit()
            self.assertIsRNGAmbiguous(transfer, False)

            unit3 = testutils.create_archive_unit(transfer, user_cardinality=u'0..1')[0]
            cnx.commit()
            self.assertIsRNGAmbiguous(transfer, True)
            self.assertErrorOn(doctor, 'rng_ambiguity', [(transfer, 'seda_archive_units_tab')])

            unit3.cw_delete()
            cnx.commit()
            self.assertIsRNGAmbiguous(transfer, False)

    def test_multiple_child_unhandled_cardinality_sub_archive_unit(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            doctor = transfer.cw_adapt_to('ISEDACompatAnalyzer')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            testutils.create_archive_unit(unit_alt_seq, user_cardinality=u'1..n')
            testutils.create_archive_unit(unit_alt_seq, user_cardinality=u'1..n')
            cnx.commit()

            self.assertIsRNGAmbiguous(transfer, True)
            self.assertErrorOn(doctor, 'rng_ambiguity', [(unit, 'seda_archive_units_tab')])

    def test_multiple_child_unhandled_cardinality_document(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            doctor = transfer.cw_adapt_to('ISEDACompatAnalyzer')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            testutils.create_data_object(unit_alt_seq, user_cardinality=u'0..n',
                                         seda_binary_data_object=transfer)
            bdo = testutils.create_data_object(unit_alt_seq, user_cardinality=u'1..n',
                                               seda_binary_data_object=transfer)
            cnx.commit()
            self.assertIsRNGAmbiguous(transfer, True)
            self.assertErrorOn(doctor, 'rng_ambiguity', [(unit, 'seda_data_objects_tab'),
                                                         (transfer, 'seda_data_objects_tab')])
            _delete_data_object(bdo)
            cnx.commit()
            self.assertIsRNGAmbiguous(transfer, False)

            # test data objects cardinality is considered globally to the profil
            # **if it's not a simplified profile**
            unit2, unit2_alt, unit2_alt_seq = testutils.create_archive_unit(transfer)
            bdo = testutils.create_data_object(unit2_alt_seq, user_cardinality=u'0..n',
                                               seda_binary_data_object=transfer)
            cnx.commit()
            self.assertIsRNGAmbiguous(transfer, True)
            self.assertErrorOn(doctor, 'rng_ambiguity', [(transfer, 'seda_data_objects_tab')])
            _delete_data_object(bdo)
            cnx.commit()
            self.assertIsRNGAmbiguous(transfer, False)

            # though adding a data object with card != 1 to another archive unit
            # **on a simplified profile** is fine
            transfer.cw_set(simplified_profile=True)
            testutils.create_data_object(unit2_alt_seq, user_cardinality=u'0..n',
                                         seda_binary_data_object=transfer)
            cnx.commit()
            self.assertErrorOn(doctor, 'rng_ambiguity', [])
            self.assertIsRNGAmbiguous(transfer, False)

    def test_multiple_child_unhandled_cardinality_keyword(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            doctor = transfer.cw_adapt_to('ISEDACompatAnalyzer')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            cnx.create_entity('SEDAKeyword', seda_keyword=unit_alt_seq,
                              user_cardinality=u'1..n')
            cnx.create_entity('SEDAKeyword', seda_keyword=unit_alt_seq,
                              user_cardinality=u'1..n')
            cnx.commit()

            self.assertErrorOn(doctor, 'rng_ambiguity', [(unit, 'seda_indexation_tab')])

    def test_single_cardinality_not_first(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            doctor = transfer.cw_adapt_to('ISEDACompatAnalyzer')
            u1 = testutils.create_archive_unit(transfer, user_cardinality=u'1..n')
            u2 = testutils.create_archive_unit(transfer, user_cardinality=u'1')
            cnx.commit()
            self.assertEqual(u1[0].ordering, 1)
            self.assertEqual(u2[0].ordering, 2)
            self.assertEqual(u1[0].user_cardinality, '1..n')
            self.assertEqual(u2[0].user_cardinality, '1')
            self.assertIsRNGAmbiguous(transfer, True)
            self.assertErrorOn(doctor, 'rng_mandatory_not_first',
                               [(transfer, 'seda_archive_units_tab')])

    def assertErrorOn(self, doctor, error_id, expected_errors):
        errors = set()
        for error in doctor.detect_problems():
            if error.rule_id == error_id:
                errors.add((error.entity, error.tab_id))

        self.assertEqual(errors, set(expected_errors))

    def assertIsRNGAmbiguous(self, transfer, ambiguous):
        transfer.cw_clear_all_caches()
        if ambiguous:
            self.assertNotIn('RNG', transfer.compat_list)
        else:
            self.assertIn('RNG', transfer.compat_list)


def _delete_data_object(data_object):
    for ref in data_object.reverse_seda_data_object_reference_id:
        ref.cw_delete()
    data_object.cw_delete()


if __name__ == '__main__':
    import unittest
    unittest.main()
