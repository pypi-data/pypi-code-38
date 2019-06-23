from unittest import TestCase, mock
from parameterized import parameterized
from bebanjo.things import ThingFetcher, Collection
from bebanjo import MovidaAPI
from .utils import titles_from_file

# pylint: disable=protected-access,too-many-arguments

def file_contents(fn):
    with open('tests/__files/' +  fn, 'rb') as f:
        bstr = f.read()
    return bstr


class TestCollection(TestCase):

    def setUp(self):
        self.titles = titles_from_file('titles_3pp_p1.xml')

    def test_is_type_collection(self):
        assert isinstance(self.titles, Collection)

    def test_collection_urls(self):
        self.assertRegex(self.titles.url, '.*/api/titles')
        self.assertEqual(self.titles.summary_url, '//titles')

    def test_member_count(self):
        self.assertEqual(len(self.titles.members), 3)
        self.assertEqual(len(self.titles), 3)

    def test_get_member_by_id(self):
        for _id in range(1001, 1003):
            assert self.titles.get_member(_id)
        assert self.titles.get_member(9988283) is None

    def test_get_members_keys_method(self):
        count = 0
        for i in self.titles.keys():
            assert isinstance(self.titles[i], ThingFetcher)
            count += 1
        assert count == 3
        with self.assertRaises(KeyError):
            _ = self.titles[3874387438]


class TestCollectionPaginationIngest(TestCase):

    @parameterized.expand([
        ('titles_3pp_p1.xml', 2, 3, 8, 3),
        ('titles_3pp_p2.xml', 3, 3, 8, 3),
        ('titles_3pp_p3.xml', 0, 2, 8, 3),
        ('titles_7pp_p1.xml', 2, 7, 8, 7),
        ('titles_7pp_p2.xml', 0, 1, 8, 7),
        ('titles_50pp_p1.xml', 0, 8, 8, 50),  # no page links, so no
        ('titles_9pp_p1.xml', 0, 8, 8, 50),  # update to default 50 pp
    ])
    def test_get_titles_paginated(self, url, nxt, count, ia, pp):
        titles = titles_from_file(url)
        self.assertEqual(len(titles), count)
        self.assertEqual(titles.items_available, ia)
        if nxt:
            self.assertEqual(titles.next_page, nxt)
        self.assertEqual(titles.per_page, pp)


class TestCollectionPaginationItteration(TestCase):

    def setUp(self):
        self.mapi = MovidaAPI(url='http://localhost:8080/api')
        patcher = mock.patch('urllib.request.urlopen')
        self.mock_urlopen = patcher.start()
        self.addCleanup(patcher.stop)

    @parameterized.expand(
        [
            (1, 1001, 3, 3, (1, 2, 3)),
            (2, 1004, 3, 3, (2, 3)),
            (3, 1007, 3, 3, (3, )),
            (1, 1001, 7, 2, (1, 2)),
            (2, 1008, 7, 2, (2, )),
            (1, 1001, 50, 1, (1, )),  # pp not defined in returned pages
            (1, 1001, 50, 1, (1, )),  # next or prev so will default to 50
        ]
    )
    def test_get_titles_pagination_itteration(self, start_page, ide, pp, count, pn):
        pages = [file_contents(f'titles_{pp}pp_p{p}.xml') for p in pn]
        cm = mock.MagicMock()
        cm.read = lambda: pages.pop(0)
        cm.getcode.return_value = 200
        self.mock_urlopen.return_value = cm
        titles = self.mapi.titles.get_paginated(page=start_page, per_page=pp)
        assert titles is self.mapi.titles
        id_expected = ide
        for title in self.mapi.titles:
            assert title.id == id_expected
            id_expected += 1
        assert id_expected == 1009
        self.assertEqual(titles.items_available, 8)
        self.assertEqual(titles.count_pages, count)
        self.assertEqual(titles.per_page, pp)
