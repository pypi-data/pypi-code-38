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
"""cubicweb-seda unit tests for XSD profile generation"""

from collections import namedtuple

from lxml import etree

from cubicweb.devtools.testlib import CubicWebTC

from test_profile_generation import XmlTestMixin, SEDAExportFuncTCMixIn


AttrDef = namedtuple('AttrDef', ['label', 'card', 'value'])


class SEDAHTMLExportFuncTC(SEDAExportFuncTCMixIn, XmlTestMixin, CubicWebTC):
    adapter_id = 'SEDA-2.0.html'

    def setup_database(self):
        super(SEDAHTMLExportFuncTC, self).setup_database()
        with self.admin_access.cnx() as cnx:
            scheme = cnx.find('ConceptScheme', title=u'Keyword Types').one()
            some_concept = scheme.reverse_in_scheme[0]
            lang_rtype = cnx.find('CWRType', name='seda_language_to').one()
            some_concept.scheme.cw_set(scheme_relation_type=lang_rtype)
            cnx.find('SEDALanguage').one().cw_set(seda_language_to=some_concept)
            cnx.find('SEDAKeywordReference').one().cw_set(
                seda_keyword_reference_to=some_concept,
                seda_keyword_reference_to_scheme=some_concept.scheme)
            cnx.commit()

        self.concept_eid = some_concept.eid

    def assertXmlValid(self, root):
        pass  # no schema available for html 5

    def get_element(self, profile, name):
        elements = self.xpath(profile, '//h3[text()="{0}"]'.format(name))
        self.assertEqual(len(elements), 1)
        return elements[0].getparent()

    def element_values(self, element):
        el_defs = []
        for div in self.xpath(element, 'div'):
            el_def = {}
            el_defs.append(el_def)
            for span in self.xpath(div, 'span'):
                if len(span):
                    value = etree.tostring(span[0])
                else:
                    value = span.text
                el_def[span.attrib['class']] = value
        return el_defs

    def test_profile1(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.entity_from_eid(self.transfer_eid)
            some_concept = cnx.entity_from_eid(self.concept_eid)
            profile = self.profile_etree(transfer)
            # ensure encoding is declared
            meta = self.xpath(profile, '/html/head/meta')[0]
            self.assertEqual(meta.attrib, {'content': 'text/html; charset=UTF-8',
                                           'http-equiv': 'content-type'})
            # ensure only one first level title
            self.assertEqual(len(self.xpath(profile, '//title')), 1)
            self.assertEqual(len(self.xpath(profile, '//h1')), 1)
            # ensure annotation are serialized
            self.assertEqual(
                [ann for ann in self.xpath(profile, '//div[@class="description"]/text()')
                 if ann != 'data object title'],
                ['Composant ISAD(G)'])
            # ensure all attributes have label, card and value defined
            attr_divs = self.xpath(profile, '//div[@class="attribute"]')
            attr_defs = set()
            for attr_div in attr_divs:
                attr_def = AttrDef(self.xpath(attr_div, 'span[@class="label"]')[0].text,
                                   self.xpath(attr_div, 'span[@class="card"]')[0].text,
                                   self.xpath(attr_div, 'span[@class="value"]')[0].text)
                attr_defs.add(attr_def)
            self.assertEqual(attr_defs, set([
                AttrDef(label='algorithm', card='mandatory', value=None),
                AttrDef(label='filename', card='optional', value=None),
                AttrDef(label='id', card='mandatory', value='id{}'.format(self.au_eid)),
                AttrDef(label='id', card='mandatory', value='id{}'.format(self.bdo_eid)),
                AttrDef(label='id', card='optional', value=None),
                AttrDef(label='when', card='optional', value=None),
                AttrDef(label='uri', card='optional', value=None),
            ]))
            # ensure jumped element children have proper parent
            clv = self.get_element(profile, 'CodeListVersions')
            self.assertEqual(len(self.xpath(clv, 'div/h3[text()="MimeTypeCodeListVersion"]')), 1)
            # ensure KeywordType list handling
            ktype = self.get_element(profile, 'KeywordType')
            el_defs = self.element_values(ktype)
            self.assertEqual(el_defs, [{'label': 'listVersionID', 'value': 'edition 2009'},
                                       {'label': 'XSD content type', 'value': 'xsd:token'}])
            # KeywordReference
            kref = self.get_element(profile, 'KeywordReference')
            el_defs = self.element_values(kref)
            concept_link = '<a href="{0}">md5</a>'.format(some_concept.absolute_url())
            scheme = some_concept.scheme
            scheme_link = '<a href="{0}">Keyword Types</a>'.format(scheme.absolute_url())
            self.assertEqual(el_defs, [{'label': 'schemeURI', 'value': scheme_link},
                                       {'label': 'XSD content type', 'value': 'xsd:token'},
                                       {'label': 'fixed value', 'value': concept_link}])
            # Language
            lang = self.get_element(profile, 'Language')
            el_defs = self.element_values(lang)
            self.assertEqual(el_defs, [{'label': 'XSD content type', 'value': 'xsd:language'},
                                       {'label': 'fixed value', 'value': concept_link}])


if __name__ == '__main__':
    import unittest
    unittest.main()
