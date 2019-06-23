from unittest import TestCase, mock
from bebanjo.utils import inspect
from bebanjo.things import ThingFetcher, Metadata
from .utils import title_from_file

# pylint: disable=protected-access


class TestTitleConstruction(TestCase):

    def test_title_construction(self):
        title = title_from_file()
        assert title.id == 1001
        assert title['external_id'] == '63056'
        assert title['name'] == 'Winter Is Coming'
        assert isinstance(title.metadata, Metadata)
        assert len(title.metadata['subgenres']) == 2
        assert isinstance(title, ThingFetcher)
        assert isinstance(title.images, ThingFetcher)
        assert isinstance(title._meta1, dict)
        assert isinstance(title.metadata, (dict, Metadata))
        assert title.url == 'http://localhost:8080/api/titles/1001'
        assert title.summary_url == '//titles/1001'
        assert title.id == 1001
        with self.assertRaises(KeyError):
            _ = title['id']

    @mock.patch('sys.stdout')
    def test_inspect(self, mock_std_out):
        title = title_from_file()
        inspect(title)
        out_str = mock_std_out.mock_calls[0][1][0]
        assert r"Instance of Title (//titles/1001)" in out_str
        assert "> name: 'Winter Is Coming" in out_str
        assert "Metadata:" in out_str
        assert "> short_description" in out_str
        assert r"Getters:" in out_str
        assert "> images" in out_str


class TestThingFetcherFeatures(TestCase):

    def test_hop_schedule_schedulings(self):
        title = title_from_file()
        assert isinstance(title.schedule, ThingFetcher)
        schedulings = title.schedule.add_link('schedulings')
        assert isinstance(schedulings, ThingFetcher)
        assert schedulings.url == title.url + '/schedule/schedulings'
