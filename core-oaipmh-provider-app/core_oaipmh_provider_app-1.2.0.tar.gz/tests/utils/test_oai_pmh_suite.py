from django.test import SimpleTestCase
from xml_utils.xsd_tree.xsd_tree import XSDTree


class TestOaiPmhSuite(SimpleTestCase):
    def check_tag_exist(self, text, check_tag):
        tag_found = False
        for tag in XSDTree.iterfind(text, './/{http://www.openarchives.org/OAI/2.0/}' + check_tag):
            tag_found = True
        self.assertTrue(tag_found)

    def check_tag_error_code(self, text, error):
        self.check_tag_exist(text, 'error')
        for tag in XSDTree.iterfind(text, './/{http://www.openarchives.org/OAI/2.0/}error'):
            self.assertEqual(tag.attrib['code'], error)

    def check_tag_count(self, text, checkTag, number):
        count = 0
        for tag in XSDTree.iterfind(text, './/{http://www.openarchives.org/OAI/2.0/}' + checkTag):
            count += 1
        self.assertEquals(number, count)