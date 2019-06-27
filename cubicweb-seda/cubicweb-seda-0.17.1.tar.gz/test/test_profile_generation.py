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
"""cubicweb-seda unit tests for XSD profile generation.

You may want to set the TEST_WRITE_SEDA_FILES environment variable to activate
writing of generated content back to the file-system.
"""

from doctest import Example
from itertools import chain, izip, repeat
import os
from os.path import basename, join
import unittest

from six import binary_type, text_type

from lxml import etree
from lxml.doctestcompare import LXMLOutputChecker

from logilab.common.decorators import cached

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_seda.xsd2yams import XSDMMapping
from cubicweb_seda.entities import profile_generation as pg

from cubicweb_seda import testutils


class XmlTestMixin(object):
    """Mixin class providing additional assertion methods for checking XML data."""
    NAMESPACES = {
        'xs': 'http://www.w3.org/2001/XMLSchema',
        'seda': 'fr:gouv:culture:archivesdefrance:seda:v2.0',
        'rng': 'http://relaxng.org/ns/structure/1.0',
        'a': 'http://relaxng.org/ns/compatibility/annotations/1.0',
    }
    # TBD in concret implementation
    schema_class = None
    schema_file = None
    adapter_id = None

    @classmethod
    @cached
    def schema(cls, xsd_filename):
        with open(xsd_filename) as stream:
            return cls.schema_class(etree.parse(stream))

    def xpath(self, element, expression):
        return element.xpath(expression, namespaces=self.NAMESPACES)

    def get_element(self, profile, name):
        """Return etree element definition for 'name' (there should be only one)"""
        elements = self.get_elements(profile, name)
        self.assertEqual(len(elements), 1)
        return elements[0]

    def get_elements(self, profile, name):
        """Return etree element definitions for 'name'"""
        raise NotImplementedError()

    def get_attribute(self, profile, name):
        """Return etree attribute definition for 'name' (there should be only one)"""
        attributes = self.get_attributes(profile, name)
        self.assertEqual(len(attributes), 1)
        return attributes[0]

    def get_attributes(self, profile, name):
        """Return etree attribute definitions for 'name'"""
        raise NotImplementedError()

    def profile_etree(self, transfer_entity, adapter_id=None):
        """Return etree representation of profile's XSD for the given transfer entity."""
        adapter = transfer_entity.cw_adapt_to(adapter_id or self.adapter_id)
        root = adapter.dump_etree()
        self.assertXmlValid(root)
        return root

    def assertXmlValid(self, root):
        """Validate an XML etree according to an XSD file (.xsd)."""
        schema = self.schema(self.datapath(self.schema_file))
        schema.assert_(root)

    def assertXmlEqual(self, actual, expected):
        """Check that both XML strings represent the same XML tree."""
        checker = LXMLOutputChecker()
        if not checker.check_output(expected, actual, 0):
            message = checker.output_difference(Example("", expected), actual, 0)
            self.fail(message)

    def check_xsd_profile(self, root, sample_file, **substitutions):
        """Check that the SEDA profile can be used to validate a sample XML document."""
        if os.environ.get('TEST_WRITE_SEDA_FILES'):
            fname = join('/tmp', basename(sample_file))
            with open(fname, 'w') as stream:
                stream.write(etree.tostring(root, pretty_print=True))
            print('Generated profile saved to {}'.format(fname))
        profile = self.schema_class(root)
        with open(sample_file) as f:
            sample_xml_string = f.read().format(**substitutions)
        profile.assert_(etree.fromstring(sample_xml_string))


class XMLSchemaTestMixin(XmlTestMixin):
    """Mixin extending XmlTestMixin with implementation of some assert methods for XMLSchema."""

    schema_class = etree.XMLSchema
    schema_file = 'XMLSchema.xsd'
    adapter_id = 'SEDA-2.0.xsd'

    def get_elements(self, profile, name):
        return self.xpath(profile, '//xs:element[@name="{0}"]'.format(name))

    def get_attributes(self, profile, name):
        return self.xpath(profile, '//xs:attribute[@name="{0}"]'.format(name))

    def assertElementDefinition(self, element, expected):
        edef = dict(element.attrib)
        types = self.xpath(element, 'xs:complexType/xs:simpleContent/xs:extension')
        assert len(types) <= 1
        if types:
            edef['type'] = types[0].attrib['base']
        self.assertEqual(edef, expected)

    def assertAttributeDefinition(self, element, expected):
        edef = dict(element.attrib)
        edef.setdefault('use', 'required')
        self.assertEqual(edef, expected)

    def assertXSDAttributes(self, element, expected_attributes):
        # attributes for regular elements
        attrs = [x.attrib for x in self.xpath(element, 'xs:complexType/xs:attribute')]
        # attributes for simple elements
        attrs += [x.attrib for x in self.xpath(
            element, 'xs:complexType/xs:simpleContent/xs:extension/xs:attribute')]
        self.assertEqual(sorted(attrs), expected_attributes)


class RelaxNGTestMixin(XmlTestMixin):
    """Mixin extending XmlTestMixin with implementation of some assert methods for RelaxNG."""

    schema_class = etree.RelaxNG
    schema_file = 'relaxng.rng'
    adapter_id = 'SEDA-2.0.rng'

    def get_elements(self, profile, name):
        return self.xpath(profile, '//rng:element[@name="{0}"]'.format(name))

    def get_attributes(self, profile, name):
        return self.xpath(profile, '//rng:attribute[@name="{0}"]'.format(name))

    def assertElementDefinition(self, element, expected):
        edef = dict(element.attrib)  # {name: element name}
        if element.getparent().tag == '{http://relaxng.org/ns/structure/1.0}optional':
            edef['minOccurs'] = '0'
        elif element.getparent().tag == '{http://relaxng.org/ns/structure/1.0}oneOrMore':
            edef['maxOccurs'] = 'unbounded'
        elif element.getparent().tag == '{http://relaxng.org/ns/structure/1.0}zeroOrMore':
            edef['minOccurs'] = '0'
            edef['maxOccurs'] = 'unbounded'
        refs = self.xpath(element, 'rng:ref')
        if refs:
            assert len(refs) == 1
            edef['type'] = refs[0].attrib['name']
        self._element_fixed_value(edef, element)
        self.assertEqual(edef, expected)

    def assertAttributeDefinition(self, element, expected):
        edef = dict(element.attrib)  # {name: element name}
        if element.getparent().tag == '{http://relaxng.org/ns/structure/1.0}optional':
            edef['use'] = 'optional'
        else:
            edef['use'] = 'required'
        self._element_fixed_value(edef, element)
        self.assertEqual(edef, expected)

    def assertXSDAttributes(self, element, expected_attributes):
        adefs = []
        optattrs = self.xpath(element, 'rng:optional/rng:attribute')
        attrs = self.xpath(element, 'rng:attribute')
        for use, adef_element in chain(izip(repeat('optional'), optattrs),
                                       izip(repeat('required'), attrs)):
            adef = dict(adef_element.attrib)
            adef['use'] = use
            data_elements = self.xpath(adef_element, 'rng:data')
            if data_elements:
                assert len(data_elements) == 1
                adef['type'] = 'xsd:' + data_elements[0].attrib['type']
            self._element_fixed_value(adef, adef_element)
            adefs.append(adef)
        return sorted(adefs)

    def _element_fixed_value(self, edef, element):
        values = self.xpath(element, 'rng:value')
        if values:
            assert len(values) == 1
            value = values[0]
            edef['fixed'] = value.text
            if value.attrib.get('type'):
                edef['type'] = 'xsd:' + value.attrib['type']
        else:
            datatypes = self.xpath(element, 'rng:data')
            if datatypes:
                assert len(datatypes) == 1
                datatype = datatypes[0]
                edef['type'] = 'xsd:' + datatype.attrib['type']


class PathTargetValuesTC(CubicWebTC):

    def test_keyword_path(self):
        element_defs = iter(XSDMMapping('Keyword'))
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity
            kw = create('SEDAKeyword', user_cardinality=u'0..n')
            kt = create('SEDAKeywordType', seda_keyword_type_from=kw)

            edef = next(element_defs)
            # self.assertEqual(
            #  readable_edef(edef),
            #  ('Keyword', 'SEDAKeyword', [
            #      ('id', [('seda_id', 'object', 'SEDAid'),
            #              ('id', 'subject', 'String')]),
            #      ('KeywordContent', []),
            #      ('KeywordReference',
            #       [('seda_keyword_reference_from', 'object', 'SEDAKeywordReference'),
            #        ('seda_keyword_reference_to', 'subject', 'Concept')]),
            #      ('KeywordType', [('seda_keyword_type_from', 'object', 'SEDAKeywordType'),
            #                       ('seda_keyword_type_to', 'subject', 'Concept')]),
            #  ]))
            path = edef[-1][0][1]
            target_values = pg._path_target_values(kw, path)
            self.assertEqual(len(target_values), 1)
            target_value = target_values[0]
            self.assertEqual(target_value[0], None)
            self.assertEqual(target_value[1], None)

            path = edef[-1][2][1]
            target_values = pg._path_target_values(kw, path)
            self.assertEqual(len(target_values), 0)

            path = edef[-1][3][1]
            target_values = pg._path_target_values(kw, path)
            self.assertEqual(len(target_values), 1)
            target_value = target_values[0]
            self.assertEqual(target_value[0].eid, kt.eid)
            self.assertEqual(target_value[1], None)

            kt_scheme = testutils.scheme_for_rtype(cnx, 'seda_keyword_type_to', u'theme')
            kw_type = kt_scheme.reverse_in_scheme[0]
            kt.cw_set(seda_keyword_type_to=kw_type)
            path = edef[-1][3][1]
            target_values = pg._path_target_values(kw, path)
            self.assertEqual(len(target_values), 1)
            target_value = target_values[0]
            self.assertEqual(target_value[0].eid, kt.eid)
            self.assertEqual(target_value[1].eid, kw_type.eid)

            edef = next(element_defs)
            # self.assertEqual(
            #     readable_edef(edef),
            #     ('KeywordContent', 'SEDAKeyword', [
            #         ('KeywordContent', [('keyword_content', 'subject', 'String')]),
            #     ]))
            path = edef[-1][0][1]
            target_values = pg._path_target_values(kw, path)
            self.assertEqual(len(target_values), 1)
            target_value = target_values[0]
            self.assertEqual(target_value[0], None)
            self.assertEqual(target_value[1], None)

    def test_internal_reference(self):
        element_defs = iter(XSDMMapping('DataObjectReference'))
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity
            transfer = create('SEDAArchiveTransfer', title=u'test profile')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(
                transfer)
            bdo = cnx.create_entity('SEDABinaryDataObject',
                                    user_annotation=u'I am mandatory',
                                    seda_binary_data_object=transfer)
            ref = create('SEDADataObjectReference', seda_data_object_reference=unit_alt_seq,
                         seda_data_object_reference_id=bdo)

            edef = next(element_defs)
            # readable_edef(edef)
            # ('DataObjectReference',
            #  'SEDADataObjectReference',
            #  [('id', [('seda_id', 'object', 'SEDAid'), ('id', 'subject', 'String')]),
            #   ('DataObjectReferenceId',
            #    [('seda_data_object_reference_id',
            #      'subject',
            #      ('SEDABinaryDataObject', 'SEDAPhysicalDataObject'))])])

            path = edef[-1][1][1]
            target_values = pg._path_target_values(ref, path)
            self.assertEqual(len(target_values), 1)
            target_value = target_values[0]
            self.assertEqual(target_value[0], None)
            self.assertEqual(target_value[1].eid, bdo.eid)

    def test_integrity_cardinality(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            bdo = cnx.create_entity('SEDABinaryDataObject',
                                    user_annotation=u'I am mandatory',
                                    seda_binary_data_object=transfer)
            assert pg.integrity_cardinality(bdo) == '1'
            bdo = cnx.create_entity('SEDABinaryDataObject',
                                    user_cardinality=u'0..1',
                                    user_annotation=u'opt',
                                    seda_binary_data_object=transfer)
            assert pg.integrity_cardinality(bdo) == '0..1'

            _, _, unit_alt_seq = testutils.create_archive_unit(
                None, cnx=cnx)
            bdo = testutils.create_data_object(unit_alt_seq)
            assert pg.integrity_cardinality(bdo) == '0..n'

            _, _, unit_alt_seq = testutils.create_archive_unit(
                None, cnx=cnx, user_cardinality=u'1..n')
            bdo = testutils.create_data_object(unit_alt_seq, user_cardinality=u'0..1')
            assert pg.integrity_cardinality(bdo) == '0..n'

            _, _, unit_alt_seq = testutils.create_archive_unit(
                None, cnx=cnx, user_cardinality=u'1..n')
            _, _, unit_alt_seq2 = testutils.create_archive_unit(
                unit_alt_seq, cnx=cnx, user_cardinality=u'0..n')
            bdo = testutils.create_data_object(unit_alt_seq2, user_cardinality=u'1')
            assert pg.integrity_cardinality(bdo) == '0..n'

            _, _, unit_alt_seq = testutils.create_archive_unit(
                None, cnx=cnx, user_cardinality=u'1')
            _, _, unit_alt_seq2 = testutils.create_archive_unit(
                unit_alt_seq, cnx=cnx, user_cardinality=u'1..n')
            bdo = testutils.create_data_object(unit_alt_seq2, user_cardinality=u'0..1')
            assert pg.integrity_cardinality(bdo) == '0..n'

            _, _, unit_alt_seq = testutils.create_archive_unit(
                None, cnx=cnx, user_cardinality=u'0..1')
            _, _, unit_alt_seq2 = testutils.create_archive_unit(
                unit_alt_seq, cnx=cnx, user_cardinality=u'1')
            bdo = testutils.create_data_object(unit_alt_seq2, user_cardinality=u'1..n')
            assert pg.integrity_cardinality(bdo) == '0..n'


class SEDA2RNGExportTC(RelaxNGTestMixin, CubicWebTC):

    def test_skipped_mandatory_simple(self):
        with self.admin_access.cnx() as cnx:
            profile = self.profile_etree(cnx.create_entity('SEDAArchiveTransfer',
                                                           title=u'test profile'))
            date = self.get_element(profile, 'Date')
            self.assertElementDefinition(date, {'name': 'Date',
                                                'type': 'xsd:dateTime'})
            self.assertXSDAttributes(date, [])
            identifier = self.get_element(profile, 'MessageIdentifier')
            self.assertElementDefinition(identifier, {'name': 'MessageIdentifier',
                                                      'type': 'xsd:token'})
            self.assertXSDAttributes(
                identifier,
                [{'name': 'schemeAgencyID', 'use': 'optional', 'type': 'xsd:token'},
                 {'name': 'schemeAgencyName', 'use': 'optional', 'type': 'xsd:string'},
                 {'name': 'schemeDataURI', 'use': 'optional', 'type': 'xsd:anyURI'},
                 {'name': 'schemeID', 'use': 'optional', 'type': 'xsd:token'},
                 {'name': 'schemeName', 'use': 'optional', 'type': 'xsd:string'},
                 {'name': 'schemeURI', 'use': 'optional', 'type': 'xsd:anyURI'},
                 {'name': 'schemeVersionID', 'use': 'optional', 'type': 'xsd:token'}])

    def test_skipped_mandatory_complex(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            testutils.create_data_object(transfer, filename=u'fixed.txt')
            profile = self.profile_etree(transfer)
            fname = self.get_element(profile, 'Filename')
            self.assertElementDefinition(fname, {'name': 'Filename',
                                                 'fixed': 'fixed.txt',
                                                 'type': 'xsd:string'})
            self.assertXSDAttributes(fname, [])
            attachment = self.get_element(profile, 'Attachment')
            self.assertElementDefinition(attachment, {'name': 'Attachment',
                                                      'type': 'xsd:base64Binary'})
            self.assertXSDAttributes(attachment,
                                     [{'name': 'filename', 'use': 'optional',
                                       'type': 'xsd:string'},
                                      {'name': 'uri', 'use': 'optional',
                                       'type': 'xsd:anyURI'}])

    def test_fileinfo_card(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            bdo = cnx.create_entity('SEDABinaryDataObject',
                                    user_annotation=u'I am mandatory',
                                    seda_binary_data_object=transfer)
            appname = cnx.create_entity('SEDACreatingApplicationName',
                                        seda_creating_application_name=bdo)

            profile = self.profile_etree(transfer)
            fileinfo = self.get_element(profile, 'FileInfo')
            self.assertElementDefinition(fileinfo, {'name': 'FileInfo'})

            appname.cw_set(user_cardinality=u'1')
            profile = self.profile_etree(transfer)
            fileinfo = self.get_element(profile, 'FileInfo')
            self.assertElementDefinition(fileinfo, {'name': 'FileInfo'})

            appname.cw_set(user_cardinality=u'0..1')
            bdo.cw_set(filename=u'fixed.txt')
            profile = self.profile_etree(transfer)
            fileinfo = self.get_element(profile, 'FileInfo')
            self.assertElementDefinition(fileinfo, {'name': 'FileInfo'})

    def test_data_object_package_card(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            bdo = cnx.create_entity('SEDABinaryDataObject',
                                    user_annotation=u'I am mandatory',
                                    seda_binary_data_object=transfer)

            profile = self.profile_etree(transfer)
            fileinfo = self.get_element(profile, 'DataObjectPackage')
            self.assertElementDefinition(fileinfo, {'name': 'DataObjectPackage'})

            bdo.cw_set(user_cardinality=u'1')
            profile = self.profile_etree(transfer)
            dop = self.get_element(profile, 'DataObjectPackage')
            self.assertElementDefinition(dop, {'name': 'DataObjectPackage'})

    def test_object_package_group(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            bdo = cnx.create_entity('SEDABinaryDataObject',
                                    user_annotation=u'I am number one',
                                    seda_binary_data_object=transfer)
            cnx.create_entity('SEDABinaryDataObject',
                              user_annotation=u'I am number two',
                              seda_binary_data_object=transfer)
            cnx.create_entity('SEDAPhysicalDataObject',
                              user_annotation=u'I am number three',
                              seda_physical_data_object=transfer)

            profile = self.profile_etree(transfer)
            dop = self.get_element(profile, 'DataObjectPackage')
            self.assertEqual(len(self.xpath(dop, './rng:group/*')), 3)

            # setting some cardinality to 1 will remove rng:optional parent of the DataObjectPackage
            # and BinaryDataObject nodes
            bdo.cw_set(user_cardinality=u'1')
            profile = self.profile_etree(transfer)
            dop = self.get_element(profile, 'DataObjectPackage')
            self.assertEqual(len(self.xpath(dop, './rng:group/*')), 3)

    def test_transfer_annotation(self):
        with self.admin_access.cnx() as cnx:
            profile = self.profile_etree(cnx.create_entity('SEDAArchiveTransfer',
                                                           title=u'test profile',
                                                           user_annotation=u'some description'))
            docs = self.xpath(profile, '///xs:documentation')
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0].text, 'some description')

    def test_transfer_signature(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            cnx.create_entity('SEDASignature', seda_signature=transfer)
            profile = self.profile_etree(transfer)
            signature = self.get_element(profile, 'Signature')
            self.assertElementDefinition(signature, {'name': 'Signature', 'type': 'OpenType'})
            self.assertOpenTypeIsDefined(profile)

    def test_keyword(self):
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity

            scheme = testutils.scheme_for_rtype(cnx, 'seda_keyword_type_to', u'theme')
            kw_type = scheme.reverse_in_scheme[0]

            transfer = create('SEDAArchiveTransfer', title=u'test profile')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(
                transfer, user_cardinality=u'0..n')

            kw = create('SEDAKeyword', seda_keyword=unit_alt_seq,
                        keyword_content=u'kwick')
            kwr_e = create('SEDAKeywordReference', seda_keyword_reference_from=kw)
            create('SEDAKeywordType', seda_keyword_type_from=kw,
                   seda_keyword_type_to=kw_type)

            profile = self.profile_etree(transfer)

            keywords = self.get_elements(profile, 'Keyword')
            self.assertElementDefinition(keywords[0], {'name': 'Keyword'})

            kwc = self.get_elements(profile, 'KeywordContent')
            self.assertElementDefinition(kwc[0], {'name': 'KeywordContent',
                                                  'type': 'xsd:string',
                                                  'fixed': 'kwick'})

            kwt = self.get_element(profile, 'KeywordType')
            self.assertElementDefinition(kwt, {'name': 'KeywordType',
                                               'type': 'xsd:token',
                                               'fixed': 'theme'})
            self.assertXSDAttributes(
                kwt,
                [{'name': 'listVersionID', 'fixed': 'seda_keyword_type_to/None vocabulary'}])
            kwr = self.get_element(profile, 'KeywordReference')
            self.assertElementDefinition(kwr, {'name': 'KeywordReference',
                                               'type': 'xsd:token'})
            self.assertXSDAttributes(
                kwr,
                [{'name': 'schemeAgencyID', 'type': 'xsd:token', 'use': 'optional'},
                 {'name': 'schemeAgencyName', 'type': 'xsd:string', 'use': 'optional'},
                 {'name': 'schemeDataURI', 'type': 'xsd:anyURI', 'use': 'optional'},
                 {'name': 'schemeID', 'type': 'xsd:token', 'use': 'optional'},
                 {'name': 'schemeName', 'type': 'xsd:string', 'use': 'optional'},
                 {'name': 'schemeURI', 'type': 'xsd:anyURI', 'use': 'optional'},
                 {'name': 'schemeVersionID', 'type': 'xsd:token', 'use': 'optional'}])

            kwr_e.cw_set(seda_keyword_reference_to_scheme=scheme)
            profile = self.profile_etree(transfer)
            kwr = self.get_element(profile, 'KeywordReference')
            self.assertElementDefinition(kwr, {'name': 'KeywordReference',
                                               'type': 'xsd:token'})
            self.assertXSDAttributes(
                kwr,
                [{'name': 'schemeURI', 'fixed': scheme.cwuri}])

            kwr_e.cw_set(seda_keyword_reference_to=kw_type)
            profile = self.profile_etree(transfer)
            kwr = self.get_element(profile, 'KeywordReference')
            self.assertElementDefinition(kwr, {'name': 'KeywordReference',
                                               'type': 'xsd:token',
                                               'fixed': kw_type.cwuri})
            self.assertXSDAttributes(
                kwr,
                [{'name': 'schemeURI', 'fixed': scheme.cwuri}])

    def test_code_list(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            scheme = cnx.create_entity('ConceptScheme', title=u'Keyword Types')
            cnx.create_entity('SEDAMimeTypeCodeListVersion',
                              seda_mime_type_code_list_version_from=transfer,
                              seda_mime_type_code_list_version_to=scheme)

            profile = self.profile_etree(transfer)
            mt_clv = self.get_element(profile, 'MimeTypeCodeListVersion')
            self.assertElementDefinition(mt_clv, {'name': 'MimeTypeCodeListVersion',
                                                  'fixed': scheme.cwuri,
                                                  'type': 'xsd:token'})
            # XXX also fix listSchemeURI ?
            self.assertXSDAttributes(
                mt_clv,
                [{'name': 'listAgencyID', 'use': 'optional', 'type': 'xsd:token'},
                 {'name': 'listAgencyName', 'use': 'optional', 'type': 'xsd:string'},
                 {'name': 'listID', 'use': 'optional', 'type': 'xsd:token'},
                 {'name': 'listName', 'use': 'optional', 'type': 'xsd:string'},
                 {'name': 'listSchemeURI', 'use': 'optional', 'type': 'xsd:anyURI'},
                 {'name': 'listURI', 'use': 'optional', 'type': 'xsd:anyURI'},
                 {'name': 'listVersionID', 'use': 'optional', 'type': 'xsd:token'}])

    def test_multiple_concepts(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            scheme = testutils.scheme_for_type(cnx, None, None,
                                               u'application/msword', u'application/pdf')
            cnx.create_entity('SEDAMimeTypeCodeListVersion',
                              seda_mime_type_code_list_version_from=transfer,
                              seda_mime_type_code_list_version_to=scheme)
            bdo = testutils.create_data_object(transfer)
            bdo.mime_type.cw_set(user_cardinality=u'1',
                                 seda_mime_type_to=scheme.reverse_in_scheme)

            profile = self.profile_etree(transfer)
            mt = self.get_element(profile, 'MimeType')
            self.assertEqual('\n'.join(etree.tostring(mt, pretty_print=True).splitlines()[1:-1]),
                             '''\
  <rng:choice>
    <rng:value type="token">application/msword</rng:value>
    <rng:value type="token">application/pdf</rng:value>
  </rng:choice>''')

    def test_seda2_concept(self):
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity
            scheme = create('ConceptScheme', title=u'Digest algorithm')
            some_concept = scheme.add_concept(label=u'md5 algorithm', language_code=u'en')
            transfer = create('SEDAArchiveTransfer', title=u'test profile')
            cnx.create_entity('SEDAMessageDigestAlgorithmCodeListVersion',
                              seda_message_digest_algorithm_code_list_version_from=transfer,
                              seda_message_digest_algorithm_code_list_version_to=scheme)
            create('SEDABinaryDataObject', user_cardinality=u'0..n',
                   user_annotation=u'I am mandatory',
                   seda_binary_data_object=transfer,
                   seda_algorithm=some_concept)

            profile = self.profile_etree(transfer)
            algo = self.get_attribute(profile, 'algorithm')
            self.assertAttributeDefinition(algo, {'name': 'algorithm',
                                                  'use': 'required',
                                                  'type': 'xsd:token',
                                                  'fixed': 'md5 algorithm'})

            create('Label', label_of=some_concept, kind=u'preferred',
                   language_code=u'seda-2', label=u'md5')

            some_concept.cw_clear_all_caches()
            profile = self.profile_etree(transfer)
            algo = self.get_attribute(profile, 'algorithm')
            self.assertAttributeDefinition(algo, {'name': 'algorithm',
                                                  'use': 'required',
                                                  'type': 'xsd:token',
                                                  'fixed': 'md5'})

    def assertOpenTypeIsDefined(self, profile):
        open_types = self.xpath(profile, '//rng:define[@name="OpenType"]')
        self.assertEqual(len(open_types), 1)

    def test_data_duplicates(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(
                transfer, user_cardinality=u'0..n')
            profile = self.profile_etree(transfer)
            title = self.get_element(profile, 'Title')
            self.assertEqual(len(self.xpath(title, 'rng:data')), 1)


class SEDAExportFuncTCMixIn(object):
    """Test that SEDA profile export works correctly."""

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity
            scheme = create('ConceptScheme', title=u'Keyword Types')
            # ensure we're able to export concept with unexpected language code
            some_concept = scheme.add_concept(label=u'md5', language_code=u'de')
            some_other_concept = scheme.add_concept(label=u'hash/md5', language_code=u'de')

            transfer = create('SEDAArchiveTransfer', title=u'test profile')
            create('SEDAMessageDigestAlgorithmCodeListVersion',
                   seda_message_digest_algorithm_code_list_version_from=transfer,
                   seda_message_digest_algorithm_code_list_version_to=scheme)
            create('SEDAFileFormatCodeListVersion',
                   seda_file_format_code_list_version_from=transfer)
            create('SEDAMimeTypeCodeListVersion',
                   user_cardinality=u'0..1',
                   seda_mime_type_code_list_version_from=transfer,
                   seda_mime_type_code_list_version_to=scheme)
            access_rule = create('SEDAAccessRule',
                                 user_cardinality=u'0..1',
                                 seda_access_rule=transfer)
            access_rule_seq = create('SEDASeqAccessRuleRule',
                                     reverse_seda_seq_access_rule_rule=access_rule)
            create('SEDAStartDate', user_cardinality=u'0..1', seda_start_date=access_rule_seq)
            # binary data object
            bdo = testutils.create_data_object(transfer, user_cardinality=u'0..n',
                                               seda_algorithm=some_concept)
            bdo.mime_type.cw_set(seda_mime_type_to=[some_concept, some_other_concept])
            create('SEDAFormatLitteral',
                   user_cardinality=u'0..1',
                   seda_format_litteral=bdo)
            create('SEDAEncoding',
                   user_cardinality=u'0..1',
                   seda_encoding_from=bdo)
            create('SEDAUri', seda_uri=bdo.seda_alt_binary_data_object_attachment)
            # first level archive unit
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(
                transfer, user_cardinality=u'0..n', user_annotation=u'Composant ISAD(G)')
            # management rules
            appraisal_rule = create('SEDAAppraisalRule', seda_appraisal_rule=unit_alt_seq)
            appraisal_rule_seq = create('SEDASeqAppraisalRuleRule',
                                        reverse_seda_seq_appraisal_rule_rule=appraisal_rule)
            create('SEDAStartDate', user_cardinality=u'0..1', seda_start_date=appraisal_rule_seq)
            access_rule = create('SEDAAccessRule', seda_access_rule=unit_alt_seq)
            create('SEDADisseminationRule', seda_dissemination_rule=unit_alt_seq)
            create('SEDAReuseRule', seda_reuse_rule=unit_alt_seq)
            create('SEDANeedAuthorization', seda_need_authorization=unit_alt_seq)
            # content
            kw = create('SEDAKeyword', user_cardinality=u'0..n', seda_keyword=unit_alt_seq)
            create('SEDAKeywordType', seda_keyword_type_from=kw)
            create('SEDAKeywordReference', seda_keyword_reference_from=kw)
            history_item = create('SEDACustodialHistoryItem',
                                  seda_custodial_history_item=unit_alt_seq)
            create('SEDAwhen',
                   user_cardinality=u'0..1',
                   seda_when=history_item)
            version_of = create('SEDAIsVersionOf', seda_is_version_of=unit_alt_seq)
            alt2 = create('SEDAAltIsVersionOfArchiveUnitRefId',
                          reverse_seda_alt_is_version_of_archive_unit_ref_id=version_of)
            create('SEDADataObjectReference', seda_data_object_reference=alt2)
            create('SEDAOriginatingAgencyArchiveUnitIdentifier',
                   seda_originating_agency_archive_unit_identifier=unit_alt_seq)
            create('SEDATransferringAgencyArchiveUnitIdentifier',
                   seda_transferring_agency_archive_unit_identifier=unit_alt_seq)
            create('SEDADescription', seda_description=unit_alt_seq)
            create('SEDALanguage', seda_language_from=unit_alt_seq)
            create('SEDADescriptionLanguage', seda_description_language_from=unit_alt_seq)
            create('SEDACreatedDate', seda_created_date=unit_alt_seq)
            create('SEDAEndDate', seda_end_date=unit_alt_seq)
            create('SEDADataObjectReference', user_cardinality=u'0..n',
                   seda_data_object_reference=unit_alt_seq,
                   seda_data_object_reference_id=bdo)

            cnx.commit()
        self.transfer_eid = transfer.eid
        self.bdo_eid = bdo.eid
        self.bdo_xmlid = bdo.cw_adapt_to('IXmlId').id()
        self.au_eid = unit.eid

    def test_profile1(self):
        """Check a minimal SEDA profile validating BV2.0_min.xml."""
        with self.admin_access.cnx() as cnx:
            mda_scheme = cnx.find('ConceptScheme', title=u'Keyword Types').one()
            transfer = cnx.entity_from_eid(self.transfer_eid)
            root = self.profile_etree(transfer)
        self.check_xsd_profile(root, self.datapath('BV2.0_min.xml'),
                               mda_scheme_url=mda_scheme.cwuri)
        # ensure jumped element without content are not there
        self.assertEqual(len(self.get_elements(root, 'Gps')), 0)
        # ensure element with skipped value are not there
        self.assertEqual(len(self.get_elements(root, 'TransactedDate')), 0)
        self.assertProfileDetails(root)


class SEDARNGExportFuncTC(SEDAExportFuncTCMixIn, RelaxNGTestMixin, CubicWebTC):

    def assertProfileDetails(self, root):
        # ensure profile's temporary id are exported in xml:id attribute
        self.assertEqual(len(self.xpath(root, '//rng:attribute[@xml:id]')), 2)
        for attrdef in self.xpath(root, '//xs:attribute[@xml:id]'):
            self.assertEqual(attrdef[0]['type'], 'ID')
        # ensure they are properly referenced using 'default' attribute
        references = self.xpath(root, '//rng:element[@a:defaultValue="{}"]'.format(self.bdo_xmlid))
        self.assertEqual(len(references), 1)
        self.assertEqual(references[0].attrib['name'], 'DataObjectReferenceId')
        for reference_id in self.xpath(root, '//rng:element[@name="DataObjectReferenceId"]'):
            self.assertEqual(reference_id[0].attrib['type'], 'NCName')
        # ensure optional id are properly reinjected
        references = self.xpath(root,
                                '//rng:element[@name="Keyword"]/rng:optional'
                                '/rng:attribute[@name="id"]')
        self.assertEqual(len(references), 1)
        # ensure custodial item content type is properly serialized
        chi = self.xpath(root, '//rng:element[@name="CustodialHistoryItem"]')
        self.assertEqual(len(chi), 1)
        self.assertXSDAttributes(
            chi[0],
            [{'name': 'when', 'use': 'optional', 'type': 'datedateTime'}])
        # ensure types union handling
        ddt = self.xpath(root, '//rng:element[@name="CreatedDate"]/rng:choice/rng:data')
        self.assertEqual(len(ddt), 2)
        self.assertEqual(set(elmt.attrib['type'] for elmt in ddt), set(['date', 'dateTime']))


class OldSEDAExportMixin(object):
    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity

            concepts = {}
            for rtype, etype, labels in [
                    ('file_category', None, [u'fmt/123', u'fmt/987']),
                    ('seda_encoding_to', None, [u'6']),
                    ('seda_type_to', None, [u'CDO']),
                    ('seda_description_level', None, [u'file']),
                    ('seda_algorithm', 'SEDABinaryDataObject', [u'md5']),
                    ('seda_rule', 'SEDASeqAppraisalRuleRule', [u'P10Y']),
                    ('seda_rule', 'SEDASeqAccessRuleRule', [u'AR038']),
                    ('seda_final_action', 'SEDAAppraisalRule', [u'detruire']),
            ]:
                scheme = testutils.scheme_for_type(cnx, rtype, etype, *labels)
                if len(labels) == 1:
                    concepts[labels[0]] = scheme.reverse_in_scheme[0]
                else:
                    for concept in scheme.reverse_in_scheme:
                        concepts[concept.label()] = concept

            # ensure we're able to export concept with unexpected language code
            concepts['md5'].preferred_label[0].cw_set(language_code=u'de')

            agent = testutils.create_authority_record(cnx, u'bob')

            transfer = create('SEDAArchiveTransfer', title=u'my profile title &&',
                              simplified_profile=True)

            create('SEDAComment',
                   user_cardinality=u'1',
                   comment=u'my profile description &&',
                   seda_comment=transfer)

            create('SEDAAccessRule',  # XXX mandatory for seda 1.0
                   user_cardinality=u'1',
                   seda_access_rule=transfer,
                   seda_seq_access_rule_rule=create(
                       'SEDASeqAccessRuleRule', reverse_seda_start_date=create('SEDAStartDate')))
            appraisal_rule_rule = create('SEDASeqAppraisalRuleRule',
                                         seda_rule=concepts['P10Y'],
                                         user_annotation=u"C'est dans 10ans je m'en irai",
                                         reverse_seda_start_date=create('SEDAStartDate'))
            create('SEDAAppraisalRule',
                   user_cardinality=u'0..1',
                   seda_appraisal_rule=transfer,
                   seda_final_action=concepts['detruire'],
                   seda_seq_appraisal_rule_rule=appraisal_rule_rule,
                   user_annotation=u'detruire le document')

            unit, _, unit_alt_seq = testutils.create_archive_unit(transfer,
                                                                  user_cardinality=u'1..n')

            unit_alt_seq.cw_set(reverse_seda_start_date=create('SEDAStartDate',
                                                               user_cardinality=u'0..1'),
                                reverse_seda_end_date=create('SEDAEndDate',
                                                             user_cardinality=u'0..1'),
                                # XXX, value=date(2015, 2, 24)),
                                reverse_seda_description=create('SEDADescription',
                                                                user_cardinality=u'0..1'))

            kw = create('SEDAKeyword',
                        user_cardinality=u'0..n',
                        seda_keyword=unit_alt_seq)
            create('SEDAKeywordReference',
                   seda_keyword_reference_from=kw,
                   seda_keyword_reference_to=concepts['file'],
                   seda_keyword_reference_to_scheme=concepts['file'].scheme)
            create('SEDAKeywordType',
                   user_cardinality=u'0..1',
                   seda_keyword_type_from=kw)

            create('SEDAOriginatingAgency',
                   user_cardinality=u'0..1',
                   seda_originating_agency_from=unit_alt_seq,
                   seda_originating_agency_to=agent)

            create('SEDAType',
                   user_cardinality=u'0..1',
                   seda_type_from=unit_alt_seq,
                   seda_type_to=concepts['CDO'])

            chi = create('SEDACustodialHistoryItem',
                         user_cardinality=u'0..1',
                         seda_custodial_history_item=unit_alt_seq,
                         reverse_seda_when=create('SEDAwhen',
                                                  user_cardinality=u'0..1'))

            # Add a sub archive unit
            subunit2, _, subunit2_alt_seq = testutils.create_archive_unit(
                unit_alt_seq, user_cardinality=u'1')

            # Add another sub archive unit
            subunit1, _, subunit_alt_seq = testutils.create_archive_unit(
                unit_alt_seq, user_cardinality=u'1..n')

            create('SEDAAppraisalRule',
                   user_cardinality=u'0..1',
                   seda_appraisal_rule=subunit_alt_seq,
                   seda_seq_appraisal_rule_rule=create(
                       'SEDASeqAppraisalRuleRule',
                       reverse_seda_start_date=create('SEDAStartDate')))

            create('SEDAAccessRule',
                   user_cardinality=u'1',
                   user_annotation=u'restrict',
                   seda_access_rule=subunit_alt_seq,
                   seda_seq_access_rule_rule=create('SEDASeqAccessRuleRule',
                                                    reverse_seda_start_date=create('SEDAStartDate'),
                                                    seda_rule=concepts['AR038']))

            # Add minimal document to first level archive
            ref = create('SEDADataObjectReference',
                         user_cardinality=u'0..1',
                         seda_data_object_reference=unit_alt_seq)
            bdo = testutils.create_data_object(transfer, user_cardinality=u'0..n',
                                               filename=u'this_is_the_filename.pdf',
                                               seda_algorithm=concepts['md5'],
                                               reverse_seda_data_object_reference_id=ref)

            bdo.format_id.cw_set(
                user_cardinality=u'1',
                seda_format_id_to=[concepts['fmt/123'], concepts['fmt/987']])
            create('SEDAEncoding',
                   user_cardinality=u'1',
                   seda_encoding_from=bdo,
                   seda_encoding_to=concepts['6'])

            cnx.commit()

        self.transfer_eid = transfer.eid
        self.unit_eid = unit.eid
        self.subunit1_eid = subunit1.eid
        self.subunit2_eid = subunit2.eid
        self.bdo_eid = bdo.eid
        self.kw_eid = kw.eid
        self.chi_eid = chi.eid
        self.file_concept_eid = concepts['file'].eid
        self.agent_eid = agent.eid

    def _test_profile(self, adapter_id, expected_file):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.entity_from_eid(self.transfer_eid)
            file_concept = cnx.entity_from_eid(self.file_concept_eid)
            agent = cnx.entity_from_eid(self.agent_eid)

            adapter = transfer.cw_adapt_to(adapter_id)
            generated_xsd = adapter.dump()

            if os.environ.get('TEST_WRITE_SEDA_FILES'):
                orig_content = generated_xsd
                for value, key in [(file_concept.cwuri, 'concept-uri'),
                                   (file_concept.scheme.cwuri, 'scheme-uri'),
                                   (text_type(agent.eid), 'agent-id'),
                                   (agent.dc_title(), 'agent-name')]:
                    orig_content = orig_content.replace(value, '%({})s'.format(key))
                with open(self.datapath(expected_file + '.new'), 'w') as stream:
                    stream.write(orig_content)
                print('Regenerated expected file as {}.new'.format(expected_file))

            root = etree.fromstring(generated_xsd)
            self.assertXmlValid(root)
            with open(self.datapath(expected_file)) as expected:
                self.assertXmlEqual(expected.read()
                                    % {'unit-eid': binary_type(self.unit_eid),
                                       'subunit1-eid': binary_type(self.subunit1_eid),
                                       'subunit2-eid': binary_type(self.subunit2_eid),
                                       'bdo-eid': binary_type(self.bdo_eid),
                                       'kw-eid': binary_type(self.kw_eid),
                                       'chi-eid': binary_type(self.chi_eid),
                                       'concept-uri': binary_type(file_concept.cwuri),
                                       'scheme-uri': binary_type(file_concept.scheme.cwuri),
                                       'agent-id': binary_type(agent.eid),
                                       'agent-name': binary_type(agent.dc_title())},
                                    generated_xsd)
            return adapter, root


class OldSEDAXSDExportTC(XMLSchemaTestMixin, OldSEDAExportMixin, CubicWebTC):

    def test_seda_1_0(self):
        self._test_profile('SEDA-1.0.xsd', 'seda_1_export.xsd')

    def test_seda_0_2(self):
        self._test_profile('SEDA-0.2.xsd', 'seda_02_export.xsd')

    def _test_profile(self, adapter_id, expected_file):
        adapter, root = super(OldSEDAXSDExportTC, self)._test_profile(adapter_id, expected_file)
        # ensure there is no element with @type but a complex type
        namespaces = adapter.namespaces.copy()
        namespaces.pop(None)
        dates = root.xpath('//xsd:element[@name="Date"]/xsd:complexType/xsd:sequence',
                           namespaces=namespaces)
        self.assertEqual(len(dates), 0)


class OldSEDARNGExportTC(RelaxNGTestMixin, OldSEDAExportMixin, CubicWebTC):

    def test_seda_1_0(self):
        self._test_profile('SEDA-1.0.rng', 'seda_1_export.rng')

    def test_seda_0_2_rng(self):
        self._test_profile('SEDA-0.2.rng', 'seda_02_export.rng')


class OldSEDAExportTC(RelaxNGTestMixin, CubicWebTC):

    def test_seda_0_2_bordereau_ref(self):
        """Check a sample SEDA 0.2 profile validation."""
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity

            transfer = create('SEDAArchiveTransfer', title=u'test profile',
                              simplified_profile=True)
            create('SEDAComment', seda_comment=transfer)

            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            create('SEDAArchivalAgreement', seda_archival_agreement=transfer)
            create('SEDATransferringAgencyArchiveUnitIdentifier',
                   seda_transferring_agency_archive_unit_identifier=unit_alt_seq)
            create('SEDAStartDate', seda_start_date=unit_alt_seq)
            create('SEDAEndDate', seda_end_date=unit_alt_seq)
            appraisal_rule = create('SEDAAppraisalRule',
                                    user_cardinality=u'0..1',
                                    seda_appraisal_rule=unit_alt_seq)
            appraisal_rule_seq = create('SEDASeqAppraisalRuleRule',
                                        reverse_seda_seq_appraisal_rule_rule=appraisal_rule)
            create('SEDAStartDate', seda_start_date=appraisal_rule_seq)
            access_rule = create('SEDAAccessRule',
                                 user_cardinality=u'0..1',
                                 seda_access_rule=unit_alt_seq)
            access_rule_seq = create('SEDASeqAccessRuleRule',
                                     reverse_seda_seq_access_rule_rule=access_rule)
            create('SEDAStartDate', seda_start_date=access_rule_seq)

            subunit, subunit_alt, subunit_alt_seq = testutils.create_archive_unit(
                unit_alt_seq)
            create('SEDATransferringAgencyArchiveUnitIdentifier',
                   seda_transferring_agency_archive_unit_identifier=subunit_alt_seq)
            create('SEDAStartDate', seda_start_date=subunit_alt_seq)
            create('SEDAEndDate', seda_end_date=subunit_alt_seq)
            create('SEDADescription', seda_description=subunit_alt_seq)
            kw = create('SEDAKeyword', user_cardinality=u'0..n', seda_keyword=subunit_alt_seq)
            create('SEDAKeywordReference', seda_keyword_reference_from=kw)

            create('SEDASystemId', seda_system_id=subunit_alt_seq)

            bdo = testutils.create_data_object(transfer, user_cardinality=u'0..1')
            create('SEDADataObjectReference',
                   seda_data_object_reference=subunit_alt_seq,
                   seda_data_object_reference_id=bdo)
            create('SEDAEncoding', seda_encoding_from=bdo)
            bdo.mime_type.cw_set(user_cardinality=u'1')
            create('SEDADateCreatedByApplication', seda_date_created_by_application=bdo)

            cnx.commit()

            root = self.profile_etree(transfer, 'SEDA-0.2.rng')
        self.check_xsd_profile(root, self.datapath('seda_02_bordereau_ref.xml'))

    def test_xsd_children_order(self):
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity

            transfer = create('SEDAArchiveTransfer', title=u'test profile',
                              simplified_profile=True)
            create('SEDAAccessRule',  # XXX mandatory for seda 1.0
                   user_cardinality=u'1',
                   seda_access_rule=transfer,
                   seda_seq_access_rule_rule=create(
                       'SEDASeqAccessRuleRule', reverse_seda_start_date=create('SEDAStartDate')))
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(
                transfer, user_cardinality=u'0..1')
            testutils.create_archive_unit(transfer)
            testutils.create_archive_unit(unit_alt_seq)
            bdo = testutils.create_data_object(transfer)
            create('SEDADataObjectReference',
                   seda_data_object_reference=unit_alt_seq,
                   seda_data_object_reference_id=bdo)
            cnx.commit()

            # ensure Document appears before Contains in SEDA 0.2
            adapter = transfer.cw_adapt_to('SEDA-0.2.xsd')
            root = etree.Element('test-root')
            adapter.xsd_children(root, unit)
            self.assertEqual([node.attrib['name'] for node in root],
                             ['Document', 'Contains'])

            # ensure Document appears after ArchiveObject in SEDA 1
            adapter = transfer.cw_adapt_to('SEDA-1.0.xsd')
            root = etree.Element('test-root')
            adapter.xsd_children(root, unit)
            self.assertEqual([node.attrib['name'] for node in root],
                             ['ArchiveObject', 'Document'])

    def test_duplicated_format_id(self):
        with self.admin_access.cnx() as cnx:
            scheme = testutils.scheme_for_type(cnx, 'file_category', None,
                                               u'fmt/123', u'fmt/123')
            concepts = scheme.reverse_in_scheme

            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'my profile',
                                         simplified_profile=True)
            bdo = testutils.create_data_object(transfer)
            bdo.format_id.cw_set(seda_format_id_to=concepts)

            adapter = transfer.cw_adapt_to('SEDA-1.0.rng')
            root = etree.Element('test-root')
            adapter.xsd_attachment(root, bdo)

            self.assertEqual([node.text for node in self.xpath(root, '//rng:value')],
                             ['fmt/123'])


class SEDAExportUnitTest(unittest.TestCase):

    def test_concepts_languages(self):
        self.assertEqual(pg.SEDA1XSDExport.concepts_language, 'seda-1')
        self.assertEqual(pg.SEDA02XSDExport.concepts_language, 'seda-02')

    def test_concept_value(self):
        class concept:
            labels = {}

        concept.labels['fr'] = 'Bonjour'
        self.assertEqual(pg._concept_value(concept, 'seda-1'), 'Bonjour')
        concept.labels['en'] = 'Hello'
        self.assertEqual(pg._concept_value(concept, 'seda-1'), 'Hello')
        concept.labels['seda'] = 'hello'
        self.assertEqual(pg._concept_value(concept, 'seda-1'), 'hello')
        concept.labels['seda-1'] = 'hello you'
        self.assertEqual(pg._concept_value(concept, 'seda-1'), 'hello you')
        concept.labels['seda-2'] = 'good-by'
        self.assertEqual(pg._concept_value(concept, 'seda-1'), 'hello you')


if __name__ == '__main__':
    unittest.main()
