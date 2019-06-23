import re
from unittest import mock, TestCase
from bebanjo import MovidaAPI
from .utils import title_from_file

mapi = MovidaAPI(env='staging')


class TestFetch(TestCase):

    def setUp(self):
        patcher = mock.patch('bebanjo.things.ThingFetcher._get', return_value=None)
        self.mock_get = patcher.start()
        self.addCleanup(patcher.stop)

    def assert_get_correct_url(self, re_url):
        assert re.match(re_url, self.mock_get.call_args[0][0]) is not None

# tests

    def test_get_title_url(self):
        for _id in (193094357485, '19938493758455'):
            mapi.titles.fetch(_id)
            self.assert_get_correct_url(f'.*/api/titles/{_id}$')

    def test_get_title_metadata_url(self):
        title = title_from_file()
        title.metadata.fetch()
        self.assert_get_correct_url('.*/api/titles/1001/metadata$')

    def test_get_titles_url(self):
        mapi.titles.fetch()
        self.assert_get_correct_url('.*/api/titles$')

    def test_get_url_titles_exp_metadata(self):
        mapi.titles.fetch(1001, expand='metadata')
        self.assert_get_correct_url('.*/api/titles/1001[?]expand=metadata$')

    def test_get_url_title_ext_id(self):
        for _id in [93056, '93056']:
            mapi.titles.fetch(external_id=_id)
        self.assert_get_correct_url(f'.*/api/titles[?]external_id={_id}$')

    def test_get_titles_paginated_url(self):
        for page_num in (1, 111):
            mapi.titles.get_paginated(page=page_num)
        for per_page in (5, 500):
            mapi.titles.get_paginated(per_page=per_page)
        self.assert_get_correct_url(
            r'.*/api/titles[?]page=1+[&]pagination=true[&]per_page=50*$'
        )
