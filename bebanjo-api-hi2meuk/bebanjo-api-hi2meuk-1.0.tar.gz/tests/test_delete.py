from unittest import mock, TestCase
from .utils import assert_send_body_calls_match, titles_from_file, title_from_file


class TestDelete(TestCase):

    @mock.patch('bebanjo.things.send_body')
    def test_delete_child_title(self, m_send_body):
        titles = titles_from_file()
        titles.delete(1001)
        assert_send_body_calls_match(
            m_send_body,
            re_method='^DELETE$',
            re_url=r'.*/api/titles/1001$'
        )
        assert titles.get_member(1001) is None

    @mock.patch('bebanjo.things.send_body')
    def test_delete_self_title(self, m_send_body):
        title = title_from_file()
        title.delete()
        assert_send_body_calls_match(
            m_send_body,
            re_method='^DELETE$',
            re_url=r'.*/api/titles/1001$'
        )

    @mock.patch('bebanjo.things.send_body')
    def test_delete_title_child_metadata_404(self, m_send_body):
        title = title_from_file()
        title.delete('metadata')
        assert_send_body_calls_match(
            m_send_body,
            re_method='^DELETE$',
            re_url=r'.*/api/titles/1001/metadata$'
        )
        assert not title.metadata

    @mock.patch('bebanjo.things.send_body')
    def test_delete_title_self_metadata(self, m_send_body):
        title = title_from_file()
        title.metadata.delete()
        assert_send_body_calls_match(
            m_send_body,
            re_method='^DELETE$',
            re_url=r'.*/api/titles/1001/metadata$'
        )
        assert title.metadata  # does not get deleted or emptied - expected
