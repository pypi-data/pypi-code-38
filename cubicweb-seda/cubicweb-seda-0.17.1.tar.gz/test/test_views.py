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
"""cubicweb-seda unit tests for schema"""

from json import dumps
import unittest

from six import text_type

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.web import INTERNAL_FIELD_VALUE

from cubicweb_seda.xsd2yams import RULE_TYPES
from cubicweb_seda.views import archiveunit, clone, export, mgmt_rules

from cubicweb_seda import testutils


def entity_fields(fields):
    return [text_type(field.name) for field in fields
            if field.eidparam and not field.name.startswith('__')]


class ManagementRulesTC(CubicWebTC):
    def test_rule_ref_vocabulary(self):
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity

            access_scheme = create('ConceptScheme', title=u'access')
            access_concept = access_scheme.add_concept(label=u'anyone')
            cnx.commit()

            bdo = testutils.create_transfer_to_bdo(cnx)
            transfer = bdo.container[0]

            rule_base = create('SEDAAccessRule', seda_access_rule=transfer)
            rule_alt = create('SEDAAltAccessRulePreventInheritance',
                              reverse_seda_alt_access_rule_prevent_inheritance=rule_base)
            cnx.create_entity('SEDAPreventInheritance', seda_prevent_inheritance=rule_alt)
            cnx.commit()

            self.assertEqual(mgmt_rules._rule_ref_vocabulary(transfer, rule_base.cw_etype),
                             [('you must specify a scheme for seda_access_rule_code_list_version_'
                               'from_object to select a value', INTERNAL_FIELD_VALUE)])
            self.assertEqual(mgmt_rules._rule_ref_vocabulary(transfer, rule_alt.cw_etype),
                             [('you must specify a scheme for seda_access_rule_code_list_version_'
                               'from_object to select a value', INTERNAL_FIELD_VALUE)])

            create('SEDAAccessRuleCodeListVersion',
                   seda_access_rule_code_list_version_from=transfer,
                   seda_access_rule_code_list_version_to=access_scheme)
            cnx.commit()

            self.assertEqual(mgmt_rules._rule_ref_vocabulary(transfer, rule_base.cw_etype),
                             [('<no value specified>', '__cubicweb_internal_field__'),
                              (access_concept.label(), text_type(access_concept.eid))])
            self.assertEqual(mgmt_rules._rule_ref_vocabulary(transfer, rule_alt.cw_etype),
                             [('<no value specified>', '__cubicweb_internal_field__'),
                              (access_concept.label(), text_type(access_concept.eid))])

    def test_archive_unit_component_rule_ref_vocabulary(self):
        with self.admin_access.cnx() as cnx:
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=cnx)
            for rule_type in ('access', 'appraisal'):
                etype = 'SEDASeq{0}RuleRule'.format(rule_type.capitalize())
                scheme = testutils.scheme_for_type(cnx, 'seda_rule', etype)
                concept = scheme.add_concept(label=u'whatever')
                cnx.commit()

                unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=cnx)

                self.assertEqual(mgmt_rules._rule_ref_vocabulary(unit_alt_seq, etype),
                                 [('<no value specified>', '__cubicweb_internal_field__'),
                                  ('whatever', text_type(concept.eid))])


class PermissionsTC(CubicWebTC):
    """Functional test case about permissions in the web interface."""

    def test_container_permissions(self):
        """Check that a user cannot edit a SEDA profile he/she did not create."""
        alice_login = 'alice'
        bob_login = 'bob'
        with self.admin_access.cnx() as cnx:
            self.create_user(cnx, login=alice_login)
            self.create_user(cnx, login=bob_login)
            cnx.commit()
        with self.new_access(alice_login).web_request() as req:
            alice_profile = req.create_entity('SEDAArchiveTransfer', title=u'Alice Profile')
            req.cnx.commit()
        with self.new_access(bob_login).web_request() as req:
            bob_profile = req.create_entity('SEDAArchiveTransfer', title=u'Bob Profile')
            req.cnx.commit()
        with self.new_access(alice_login).web_request() as req:
            alice_profile = req.entity_from_eid(alice_profile.eid)
            bob_profile = req.entity_from_eid(bob_profile.eid)
            alice_profile_form = self.vreg['forms'].select('edition', req, entity=alice_profile)
            bob_profile_form = self.vreg['forms'].select('edition', req, entity=bob_profile)
            alice_field_names = [field.name for field in alice_profile_form.fields]
            bob_field_names = [field.name for field in bob_profile_form.fields]
            for field_name in ('title',
                               'user_annotation',
                               'seda_archival_agency',
                               'seda_transferring_agency'):
                self.assertIn(field_name, alice_field_names)
                self.assertNotIn(field_name, bob_field_names)


class RelationWidgetTC(CubicWebTC):
    """Functional test case about the relation widget."""

    def test_linkable_rset(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'Test widget')
            bdo = cnx.create_entity('SEDABinaryDataObject',
                                    user_annotation=u'I am mandatory',
                                    seda_binary_data_object=transfer)
            bdo_alt = cnx.create_entity('SEDAAltBinaryDataObjectAttachment',
                                        reverse_seda_alt_binary_data_object_attachment=bdo)
            cnx.create_entity('SEDAAttachment', seda_attachment=bdo_alt)
            compressed = cnx.create_entity('SEDACompressed', seda_compressed=bdo)
            cnx.commit()
        with self.admin_access.web_request() as req:
            compressed = req.entity_from_eid(compressed.eid)
            req.form = {'relation': 'seda_algorithm:Concept:subject',
                        'container': text_type(transfer.eid)}
            view = self.vreg['views'].select('search_related_entities', req,
                                             rset=compressed.as_rset())
            self.failIf(view.linkable_rset())
        with self.admin_access.cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'CompressionAlgorithm')
            scheme.add_concept(label=u'bz2')
            cnx.create_entity('SEDACompressionAlgorithmCodeListVersion',
                              seda_compression_algorithm_code_list_version_from=transfer,
                              seda_compression_algorithm_code_list_version_to=scheme)
            cnx.commit()
        with self.admin_access.web_request() as req:
            compressed = req.entity_from_eid(compressed.eid)
            req.form = {'relation': 'seda_algorithm:Concept:subject',
                        'container': text_type(transfer.eid)}
            view = self.vreg['views'].select('search_related_entities', req,
                                             rset=compressed.as_rset())
            self.assertEqual(len(view.linkable_rset()), 1)


class HelperFunctionsTC(CubicWebTC):
    def test_rtags_from_xsd_element(self):
        from cubicweb.web.views.uicfg import reledit_ctrl
        from cubicweb_seda.views import rtags_from_xsd_element

        rsection, display_ctrl = rtags_from_xsd_element('SEDABinaryDataObject', 'FileInfo')

        self.assertEqual(rsection.etype_get('SEDABinaryDataObject', 'filename', 'subject'),
                         None)
        self.assertEqual(reledit_ctrl.etype_get('SEDABinaryDataObject', 'filename', 'subject'),
                         {'novalue_include_rtype': False, 'novalue_label': u'<no value specified>'})


class FormatSupportedPredicateTC(CubicWebTC):

    def test_format_supported(self):
        class fakecls(object):
            def __init__(self, seda_version):
                self.seda_version = seda_version

        predicate = export.format_supported()

        with self.admin_access.web_request() as req:
            transfer = req.create_entity('SEDAArchiveTransfer', title=u'Test widget',
                                         simplified_profile=True)
            req.cnx.commit()

            for seda_version in ('2.0', '1.0', '0.2'):
                self.assertEqual(predicate(fakecls(seda_version), req, entity=transfer),
                                 1)

            self.assertEqual(predicate(fakecls(seda_version='1000'), req, entity=transfer),
                             0)

            with req.cnx.security_enabled(write=False):
                transfer.cw_set(compat_list=u'SEDA 2.0')
                req.cnx.commit()
            transfer.cw_clear_all_caches()

            self.assertEqual(predicate(fakecls(seda_version='2.0'), req, entity=transfer),
                             1)

            req.form['version'] = '2.0'  # not considered
            self.assertEqual(predicate(fakecls(seda_version='1.0'), req, entity=transfer),
                             0)

            req.form['version'] = '2.0'
            self.assertEqual(predicate(None, req, entity=transfer),
                             1)

            req.form['version'] = '1.0'
            self.assertEqual(predicate(None, req, entity=transfer),
                             0)

            del req.form['version']
            self.assertEqual(predicate(fakecls(seda_version='1.0'), req, entity=transfer,
                                       version='2.0'),
                             0)
            self.assertEqual(predicate(None, req, entity=transfer, version='2.0'),
                             1)
            self.assertEqual(predicate(None, req, entity=transfer, version='1.0'),
                             0)

            transfer.cw_set(simplified_profile=False)
            req.cnx.commit()  # will reset compat_list

            self.assertEqual(predicate(None, req, entity=transfer, version='2.0'),
                             1)
            self.assertEqual(predicate(None, req, entity=transfer, version='1.0'),
                             0)


class ArchiveTransferDiagnoseTabTC(CubicWebTC):

    def test_diagnose_tab(self):
        with self.admin_access.web_request() as req:
            transfer = req.create_entity('SEDAArchiveTransfer', title=u'diagnosis testing')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            req.cnx.commit()
            # ensure the diagnosis tab display correctly
            self.view('seda_at_diagnose_tab', req=req, rset=transfer.as_rset())


class ArchiveTransferExportTC(CubicWebTC):

    def test_selected_export_class(self):
        with self.admin_access.web_request() as req:
            transfer = req.create_entity('SEDAArchiveTransfer', title=u'diagnosis testing',
                                         simplified_profile=True)
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            req.cnx.commit()

            exporter = self.vreg['views'].select('seda.export', req, entity=transfer)
            self.assertEqual(exporter.__class__, export.SEDAExportView)

            req.form['version'] = '0.2'
            exporter = self.vreg['views'].select('seda.export', req, entity=transfer)
            self.assertEqual(exporter.__class__, export.SEDAExportView)

            req.form['version'] = '3.0'
            exporter = self.vreg['views'].select('seda.export', req, entity=transfer)
            self.assertEqual(exporter.__class__, export.SEDANonSupportedExportView)

            with req.cnx.security_enabled(write=False):
                transfer.cw_set(compat_list=u'SEDA 2.0')
                req.cnx.commit()

            req.form['version'] = '0.2'
            exporter = self.vreg['views'].select('seda.export', req, entity=transfer)
            self.assertEqual(exporter.__class__, export.SEDANonSupportedExportView)

            req.form['version'] = '2.0'
            exporter = self.vreg['views'].select('seda.export', req, entity=transfer)
            self.assertEqual(exporter.__class__, export.SEDAExportView)

    def test_export_filename(self):
        with self.admin_access.web_request() as req:
            transfer = req.create_entity('SEDAArchiveTransfer',
                                         title=u'diagnosis testing',
                                         simplified_profile=True)
            req.cnx.commit()
            for version, fmt, expected_filename in (
                ('2.0', 'rng', 'diagnosis testing-2.0.rng'),
                ('2.0', 'html', 'diagnosis testing-2.0.html'),
                ('1.0', 'rng', 'diagnosis testing-1.0.rng'),
                ('1.0', 'xsd', 'diagnosis testing-1.0.xsd'),
            ):
                req.form['version'], req.form['format'] = version, fmt
                view = self.vreg['views'].select('seda.export', req,
                                                 rset=transfer.as_rset())
                view.set_request_content_type()
                self.assertEqual(
                    view._cw.headers_out.getRawHeaders('content-disposition'),
                    ['attachment;filename="{0}"'.format(expected_filename)])


class SimplifiedFormsTC(CubicWebTC):
    """Functional test case about forms in the web interface."""

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'diagnosis testing',
                                         simplified_profile=True)
            archive_unit = testutils.create_archive_unit(transfer)[0]

            cnx.commit()
            self.transfer_eid = transfer.eid
            self.archive_unit_eid = archive_unit.eid

    def create_and_link_form(self, req, etype, linkto=None, **kwargs):
        # add minimal information in form to mimick __linkto behaviour
        if linkto is None:
            linkto = self.archive_unit_eid
        req.form['__linkto'] = 'x:{0}:y'.format(linkto)
        return self._create_etype_form(req, etype, **kwargs)

    def create_inlined_form(self, req, etype, parent=None, **kwargs):
        # add minimal information in form to mimick inlined form behaviour
        if parent is None:
            parent = self.archive_unit_eid
        req.form['arg'] = [dumps(text_type(parent))]
        return self._create_etype_form(req, etype, **kwargs)

    def _create_etype_form(self, req, etype, **kwargs):
        entity = req.vreg['etypes'].etype_class(etype)(req)
        return self.vreg['forms'].select('edition', req, entity=entity, **kwargs)

    def assertInlinedFields(self, form, expected):
        """Assert the given inlined form as the expected set of inlined forms, each defined by its
        field name and associated view class'name.
        """
        # text_type around field.name because it may be a relation schema instead of a string
        inlined_fields = [(text_type(field.name), field.view.__class__.__name__)
                          for field in form.fields if hasattr(field, 'view')]
        self.assertEqual(set(inlined_fields), set(expected))

    def assertNoRemove(self, form, field_name, role):
        """Assert the given inlined form field will be rendered without a link to remove it."""
        field = form.field_by_name(field_name, role=role)
        self.assertEqual(field.view._get_removejs(), None)

    def assertNoTitle(self, form, field_name, role):
        """Assert the given inlined form field will be rendered without form title."""
        field = form.field_by_name(field_name, role=role)
        self.assertEqual(field.view.form_renderer_id, 'notitle')

    def test_top_level_rule_form(self):
        with self.admin_access.web_request() as req:
            req.entity_from_eid(self.transfer_eid).cw_set(simplified_profile=False)
            req.cnx.commit()
            for rule_type in RULE_TYPES:
                if rule_type == 'classification':
                    continue
                with self.subTest(rule_type=rule_type):
                    form = self.create_and_link_form(
                        req, 'SEDA{0}Rule'.format(rule_type.capitalize()),
                        linkto=self.transfer_eid)
                    self.assertInlinedFields(form, [
                        ('seda_seq_{0}_rule_rule'.format(rule_type),
                         'InlineAddNewLinkView'),
                    ])
            form = self.create_and_link_form(
                req, 'SEDAClassificationRule'.format(rule_type.capitalize()),
                linkto=self.transfer_eid)
            self.assertInlinedFields(form, [
                ('seda_seq_classification_rule_rule', 'InlineAddNewLinkView'),
                ('seda_classification_reassessing_date', 'InlineAddNewLinkView'),
                ('seda_need_reassessing_authorization', 'InlineAddNewLinkView'),
            ])

    def test_top_level_rule_form_simplified(self):
        with self.admin_access.web_request() as req:
            for rule_type in ('appraisal', 'access'):
                with self.subTest(rule_type=rule_type):
                    form = self.create_and_link_form(
                        req, 'SEDA{0}Rule'.format(rule_type.capitalize()),
                        linkto=self.transfer_eid)
                    self.assertInlinedFields(form, [
                        ('seda_seq_{0}_rule_rule'.format(rule_type),
                         'RuleRuleInlineEntityCreationFormView'),
                    ])

    def test_rule_form(self):
        with self.admin_access.web_request() as req:
            for rule_type in ('access', 'appraisal'):
                form = self.create_and_link_form(req, 'SEDA{0}Rule'.format(rule_type.capitalize()))
                self.assertInlinedFields(form, [
                    ('seda_seq_{0}_rule_rule'.format(rule_type),
                     'RuleRuleInlineEntityCreationFormView'),
                ])
                self.assertNoRemove(form, 'seda_seq_{0}_rule_rule'.format(rule_type), 'subject')

    def test_rule_rule_form(self):
        with self.admin_access.web_request() as req:
            for rule_type in ('access', 'appraisal'):
                form = self.create_and_link_form(
                    req, 'SEDASeq{0}RuleRule'.format(rule_type.capitalize()))
                other_fields = [text_type(field.name)
                                for field in form.fields if not hasattr(field, 'view')]
                self.assertNotIn('user_cardinality', other_fields)
                self.assertInlinedFields(form, [
                    ('seda_start_date', 'StartDateInlineEntityCreationFormView'),
                ])
                self.assertNoRemove(form, 'seda_start_date', 'object')
                self.assertNoTitle(form, 'seda_start_date', 'object')

    def test_create_data_object_full(self):
        with self.admin_access.web_request() as req:
            req.entity_from_eid(self.transfer_eid).cw_set(simplified_profile=False)
            req.cnx.commit()
            form = self.create_inlined_form(req, 'SEDADataObjectReference', formtype='inlined')
            self.assertEqual(entity_fields(form.fields),
                             ['seda_data_object_reference_id'])

    def test_create_data_object_simplified(self):
        with self.admin_access.web_request() as req:
            form = self.create_inlined_form(req, 'SEDADataObjectReference', formtype='inlined')
            self.assertEqual(entity_fields(form.fields),
                             [])

    def test_create_data_object_from_archive_unit_component(self):
        with self.admin_access.web_request() as req:
            unit = testutils.create_archive_unit(None, cnx=req.cnx)[0]
            req.cnx.commit()
            form = self.create_inlined_form(req, 'SEDADataObjectReference', formtype='inlined',
                                            parent=unit.eid)
            self.assertEqual(entity_fields(form.fields),
                             [])


class CloneActionsTC(CubicWebTC):

    def test_archive_transfer(self):
        with self.admin_access.web_request() as req:
            transfer = req.create_entity('SEDAArchiveTransfer', title=u'test')
            unit = testutils.create_archive_unit(transfer)[0]
            req.cnx.commit()

            actions = self.pactionsdict(req, transfer.as_rset())
            self.assertIn(clone.SEDAArchiveTransferCloneAction, actions['mainactions'])

            actions = self.pactionsdict(req, unit.as_rset())
            self.assertNotIn(clone.SEDAArchiveUnitCloneAction, actions['mainactions'])

    def test_unit_component(self):
        with self.admin_access.web_request() as req:
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=req)
            subunit = testutils.create_archive_unit(unit_alt_seq)[0]
            req.cnx.commit()

            actions = self.pactionsdict(req, unit.as_rset())
            self.assertIn(clone.SEDAArchiveUnitCloneAction, actions['mainactions'])

            actions = self.pactionsdict(req, subunit.as_rset())
            self.assertNotIn(clone.SEDAArchiveUnitCloneAction, actions['mainactions'])


class CloneImportTC(CubicWebTC):
    """Tests for 'seda.doimport' controller (called from JavaScript)."""

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=cnx,
                                                                         user_cardinality=u'1',
                                                                         user_annotation=u'plop')
            bdo = testutils.create_data_object(unit_alt_seq, filename=u'file.txt')
            self.transfer_eid = transfer.eid
            self.unit_eid = unit.eid
            self.bdo_eid = bdo.eid
            cnx.commit()

    def doctypecode(self, cnx):
        return cnx.create_entity(
            'SEDADocumentTypeCode',
            seda_document_type_code_value=self.doctypecodevalue_eid)

    def test_import_one_entity(self):
        params = dict(eid=text_type(self.transfer_eid),
                      cloned=text_type(self.unit_eid))
        with self.admin_access.web_request(**params) as req:
            path, _ = self.expect_redirect_handle_request(
                req, 'seda.doimport')
            etype, eid = path.split('/')
            self.assertEqual(etype, 'SEDAArchiveTransfer'.lower())
            clone = req.execute('Any X WHERE X seda_archive_unit P, P eid %(p)s',
                                {'p': eid}).one()
            self.assertEqual([x.eid for x in clone.clone_of], [self.unit_eid])
            # Check that original entity attributes have been copied.
            self.assertEqual(clone.user_cardinality, u'1')
            self.assertEqual(clone.user_annotation, u'plop')
            # Check that data object has been copied and linked to the transfer
            seq = clone.first_level_choice.content_sequence
            bdo = seq.reverse_seda_data_object_reference[0].seda_data_object_reference_id[0]
            self.assertNotEqual(bdo.eid, self.bdo_eid)
            self.assertEqual(bdo.filename, 'file.txt')
            transfer = req.entity_from_eid(self.transfer_eid)
            transfer_bdos = [do.eid for do in transfer.reverse_seda_binary_data_object]
            self.assertEqual(transfer_bdos, [bdo.eid])

    def test_import_multiple_entities(self):
        with self.admin_access.cnx() as cnx:
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(
                None, cnx=cnx,
                user_cardinality=u'0..1', user_annotation=u'plouf')
            cnx.commit()
        to_clone = [self.unit_eid, unit.eid]
        params = dict(eid=text_type(self.transfer_eid),
                      cloned=','.join([text_type(self.unit_eid), text_type(unit.eid)]))
        with self.admin_access.web_request(**params) as req:
            path, _ = self.expect_redirect_handle_request(
                req, 'seda.doimport')
            etype, eid = path.split('/')
            self.assertEqual(etype, 'SEDAArchiveTransfer'.lower())
            rset = req.execute(
                'Any X,O WHERE X seda_archive_unit P, P eid %(p)s, X clone_of O',
                {'p': eid})
            self.assertEqual(len(rset), 2)
            self.assertCountEqual([oeid for __, oeid in rset.rows], to_clone)
            cardinalities, annotations = zip(*[
                (clone.user_cardinality, clone.user_annotation)
                for clone in rset.entities()])
            self.assertCountEqual(cardinalities, ('1', '0..1'))
            self.assertCountEqual(annotations, ('plop', 'plouf'))


class SEDATreeTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            self.transfer_eid = cnx.create_entity('SEDAArchiveTransfer',
                                                  title=u'Test',
                                                  simplified_profile=True).eid
            cnx.commit()

    def test_archiveunit_reparent_to_transfer(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.entity_from_eid(self.transfer_eid)
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            unit2 = testutils.create_archive_unit(unit_alt_seq)[0]
            cnx.commit()
            unit2.cw_adapt_to('IJQTree').reparent(transfer.eid, 0)
            cnx.commit()
            transfer.cw_clear_all_caches()
            self.assertEqual([x.eid for x in transfer.reverse_seda_archive_unit],
                             [unit2.eid, unit.eid])

    def test_archiveunit_reparent_to_archiveunit(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.entity_from_eid(self.transfer_eid)
            unit, _, unit_alt_seq = testutils.create_archive_unit(transfer)
            unit2, _, unit2_alt_seq = testutils.create_archive_unit(transfer)
            subunit, _, _ = testutils.create_archive_unit(unit2_alt_seq)
            cnx.commit()
            unit.cw_clear_all_caches()
            unit.cw_adapt_to('IJQTree').reparent(unit2.eid, 0)
            cnx.commit()
            unit2_alt_seq.cw_clear_all_caches()
            self.assertEqual([x.eid for x in unit2_alt_seq.reverse_seda_archive_unit],
                             [unit.eid, subunit.eid])

    def test_binarydataobject_reparent(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.entity_from_eid(self.transfer_eid)
            unit, _, unit_alt_seq = testutils.create_archive_unit(transfer)
            unit2, _, unit2_alt_seq = testutils.create_archive_unit(transfer)
            bdo = testutils.create_data_object(transfer)
            ref = cnx.create_entity('SEDADataObjectReference',
                                    seda_data_object_reference=unit_alt_seq,
                                    seda_data_object_reference_id=bdo)
            cnx.commit()
            bdo.cw_clear_all_caches()
            bdo.cw_adapt_to('IJQTree').reparent(unit2.eid, 0)
            cnx.commit()
            unit2_alt_seq.cw_clear_all_caches()
            self.assertEqual([x.eid for x in unit2_alt_seq.reverse_seda_data_object_reference],
                             [ref.eid])
            unit_alt_seq.cw_clear_all_caches()
            self.assertFalse(unit_alt_seq.reverse_seda_data_object_reference)

    def test_binarydataobject_reorder_full(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.entity_from_eid(self.transfer_eid)
            transfer.cw_set(simplified_profile=False)
            bdo1 = testutils.create_data_object(transfer)
            bdo2 = testutils.create_data_object(transfer)
            cnx.commit()

            transfer.cw_adapt_to('IJQTree').move_child_at_index(bdo2.eid, 0)

            transfer.cw_clear_all_caches()
            self.assertEqual([x.eid for x in transfer.reverse_seda_binary_data_object],
                             [bdo2.eid, bdo1.eid])

            bdo2.cw_clear_all_caches()
            transfer.cw_adapt_to('IJQTree').move_child_at_index(bdo2.eid, 2)

            bdo1.cw_clear_all_caches()
            bdo2.cw_clear_all_caches()

            transfer.cw_clear_all_caches()
            self.assertEqual([x.eid for x in transfer.cw_adapt_to('ITreeBase').iterchildren()],
                             [bdo1.eid, bdo2.eid])

    def test_binarydataobject_reorder_simplified(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.entity_from_eid(self.transfer_eid)
            unit, _, unit_alt_seq = testutils.create_archive_unit(transfer)
            bdo1 = testutils.create_data_object(unit_alt_seq)
            bdo2 = testutils.create_data_object(unit_alt_seq)
            cnx.commit()

            unit.cw_adapt_to('IJQTree').move_child_at_index(bdo2.eid, 0)

            transfer.cw_clear_all_caches()
            self.assertEqual([x.eid for x in unit.cw_adapt_to('ITreeBase').iterchildren()],
                             [bdo2.eid, bdo1.eid])


class FakeForm(object):
    def __init__(self, req, edited_entity):
        self._cw = req
        self.edited_entity = edited_entity


class ArchiveUnitVocabularyTC(CubicWebTC):

    def test_unit_ref_vocabulary(self):
        with self.admin_access.web_request() as req:
            transfer = req.cnx.create_entity('SEDAArchiveTransfer', title=u'Test')
            archunit, _, alt_seq = testutils.create_archive_unit(transfer)
            req.cnx.commit()
            archunit.cw_clear_all_caches()
            # actually expect a archive unit reference, but we want to test the query so any object
            # linked to the container is fine
            form = FakeForm(req, archunit)
            self.assertEqual(archiveunit.unit_ref_vocabulary(form, None),
                             [(u'archive unit title', text_type(archunit.eid))])

    def test_do_ref_vocabulary(self):
        with self.admin_access.web_request() as req:
            transfer = req.cnx.create_entity('SEDAArchiveTransfer', title=u'Test')
            bdo = testutils.create_data_object(transfer)
            req.cnx.commit()
            bdo.cw_clear_all_caches()
            # actually expect a data object reference, but we want to test the query so any object
            # linked to the container is fine
            form = FakeForm(req, bdo)
            self.assertEqual(archiveunit.do_ref_vocabulary(form, None),
                             [(u'data object title', text_type(bdo.eid))])


class SEDANavigationTC(CubicWebTC):

    def test_breadcrumbs(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            unit1 = testutils.create_archive_unit(transfer)[0]
            unit2 = testutils.create_archive_unit(None, cnx=cnx)[0]
            cnx.commit()
        with self.admin_access.web_request() as req:
            unit1 = req.entity_from_eid(unit1.eid)
            unit2 = req.entity_from_eid(unit2.eid)
            # unit1 is related to a transfer
            breadcrumbs = unit1.cw_adapt_to('IBreadCrumbs').breadcrumbs()
            expected_breadcrumbs = [transfer, unit1]
            self.assertEqual(breadcrumbs, expected_breadcrumbs)
            # unit2 is not related to a transfer, breadcrumbs leads to /sedalib.
            breadcrumbs = unit2.cw_adapt_to('IBreadCrumbs').breadcrumbs()
            expected_breadcrumbs = [
                (u'http://testing.fr/cubicweb/sedalib', u'SEDAArchiveUnit_plural'),
                unit2,
            ]
            self.assertEqual(breadcrumbs, expected_breadcrumbs)


if __name__ == '__main__':
    unittest.main()
