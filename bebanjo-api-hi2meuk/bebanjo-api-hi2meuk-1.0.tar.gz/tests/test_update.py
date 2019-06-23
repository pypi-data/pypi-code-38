from uuid import uuid4
from unittest import mock, TestCase
from .utils import assert_send_body_calls_match, FileReader, title_from_file

TITLE_1001 = 'tests/__files/title_1001.xml'


class TestUpdate(TestCase):

    @mock.patch('bebanjo.things.send_body')
    def test_title_update_meta1(self, mock_send_body):
        title = title_from_file('title_1001_exp_m.xml')
        assert title.metadata['air_date'] == '2011-04-24'
        mock_send_body.return_value = FileReader('title_1001_updated.xml')
        title.update({'name': 'ignore me'})
        assert_send_body_calls_match(
            mock_send_body,
            re_method='^PUT$',
            re_url=r'.*/api/titles/1001$',
            re_body=f'<title><name>ignore me</name></title>',
        )
        assert title.metadata['air_date'] == '2011-04-24'  # metadata should not be corrupted
        assert title['name'] == 'updated'

    @mock.patch('bebanjo.things.send_body')
    def test_update_meta1_value_is_function(self, mock_send_body):
        title = title_from_file('title_1001_exp_m.xml')
        mock_send_body.return_value = FileReader('title_1001_updated.xml')
        title.update(meta={'name': lambda: 'Yellow car'})
        assert_send_body_calls_match(
            mock_send_body,
            re_url=r'.*/api/titles/1001$',
            re_body=f'<title><name>Yellow car</name></title>'
        )

    @mock.patch('bebanjo.things.send_body')
    def test_title_update_links(self, mock_send_body):
        title = title_from_file('title_1001_exp_m.xml')
        mock_send_body.return_value = FileReader('title_1001_updated.xml')
        title.update(links={'licensor': 'api/licensors/4'})
        assert_send_body_calls_match(
            mock_send_body,
            re_method='^PUT$',
            re_url=r'.*/api/titles/1001$',
            re_body='<title><link href="api/licensors/4" rel="licensor" /></title>',
        )
        assert title.metadata['air_date'] == '2011-04-24'  # metadata should not be corrupted
        assert title['name'] == 'updated'                  # only because the response we returned

    @mock.patch('bebanjo.things.send_body')
    def test_title_update_metadata(self, mock_send_body):
        title = title_from_file('title_1001_exp_m.xml')
        assert title.metadata['short_description'] != 'updated'
        mock_send_body.return_value = FileReader('title_1001_m_updated.xml')
        title.metadata.update({'name': 'testing 123'})
        assert_send_body_calls_match(
            mock_send_body,
            re_url=r'.*/api/titles/1001/metadata$',
            re_body=f'<metadata type="document"><name>testing 123</name></metadata>'
        )
        assert title['name'] == 'Winter Is Coming'  # not changed
        assert title.metadata['short_description'] == 'updated'  # from our return value
