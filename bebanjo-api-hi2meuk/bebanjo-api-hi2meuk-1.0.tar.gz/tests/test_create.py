from unittest import mock, TestCase
from bebanjo.error import InvalidResourceError
from bebanjo import MovidaAPI
from .utils import assert_send_body_calls_match, FileReader, image_from_file, title_from_file

# pylint: disable=line-too-long

NEW_TITLE_XML = 'title_new_1555.xml'

API_URL = 'http://localhost:8080/api'
mapi = MovidaAPI(url=API_URL)


class TestCreate(TestCase):

    @mock.patch('bebanjo.things.send_body')
    def test_title_create_title(self, m_send_body):
        m_send_body.return_value = FileReader(NEW_TITLE_XML)
        new = mapi.titles.create({'name': 'John'})
        assert len(m_send_body.mock_calls) == 1
        assert_send_body_calls_match(
            m_send_body,
            re_method='^POST$',
            re_url=r'.*/api/titles$',
            re_body=r'^<title><name>John</name></title>$',
        )
        assert new.id == 1555

    @mock.patch('bebanjo.things.send_body')
    def test_title_create_target_platform(self, m_send_body):
        image = image_from_file()
        image.target_platforms.add_platforms([50, 51])
        assert len(m_send_body.mock_calls) == 2
        assert_send_body_calls_match(
            m_send_body,
            re_method='^POST$',
            re_url=r'.*/api/images/5001/target_platforms$',
            re_body=r'^<target-platforms><link href="http.*/api/platforms/5[0,1]" rel="platform" /></target-platforms>$'
        )

    @mock.patch('bebanjo.things.send_body')
    def test_raises_create_platform_on_non_target_platforms(self, m_send_body):
        title = title_from_file()
        m_send_body.return_value = lambda: b'<root />'
        with self.assertRaises(InvalidResourceError):
            title.add_platforms([50, 51])
