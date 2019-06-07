import sqlite3
from unittest.mock import patch
from tests import FakeRestResponse
from egcg_core import ncbi


def reset_cache():
    ncbi.data_cache = sqlite3.connect(':memory:')
    ncbi.cursor = ncbi.data_cache.cursor()
    ncbi._create_tables()


def test_fetch_from_eutils():
    ncbi_search_data = {'esearchresult': {'idlist': ['1337']}}
    ncbi_fetch_data = '''
        <ScientificName>Genus species</ScientificName>
        <OtherNames><CommonName>a common name</CommonName></OtherNames>
        <Rank>species</Rank>
    '''
    ncbi_fetch_data_sub_species = '''
        <ScientificName>Genus species</ScientificName>
        <OtherNames><CommonName>a common name</CommonName></OtherNames>
        <Rank>subspecies</Rank>
    '''

    patched_get = patch(
        'egcg_core.ncbi.requests.get',
        side_effect=(
            FakeRestResponse(ncbi_search_data),
            FakeRestResponse(ncbi_fetch_data),
            FakeRestResponse(ncbi_fetch_data),
            FakeRestResponse(ncbi_fetch_data)
        )
    )
    patched_get2 = patch(
        'egcg_core.ncbi.requests.get',
        side_effect=(
            FakeRestResponse(ncbi_search_data),
            FakeRestResponse(ncbi_fetch_data_sub_species),
            FakeRestResponse(ncbi_fetch_data_sub_species),
            FakeRestResponse(ncbi_fetch_data_sub_species)
        )
    )
    with patched_get as mocked_get:
        obs = ncbi.fetch_from_eutils('a_species')
        assert obs == ('1337', 'Genus species', 'a common name')
        mocked_get.assert_any_call(
            'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi',
            params={'db': 'Taxonomy', 'term': 'a_species', 'retmode': 'JSON'}
        )
        mocked_get.assert_any_call(
            'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi',
            params={'db': 'Taxonomy', 'id': '1337'}
        )
    with patched_get2:
        obs = ncbi.fetch_from_eutils('a_species')
        assert obs == ('1337', 'Genus species', 'a common name')


def test_cache():
    assert ncbi.fetch_from_cache('a species') is None
    ncbi._cache_species('a species', '1337', 'Scientific name', 'a species')
    assert ncbi.fetch_from_cache('a species') == ('a species', '1337', 'Scientific name', 'a species')
    reset_cache()


@patch('egcg_core.ncbi.fetch_from_eutils')
def test_get_species_name(mocked_fetch):
    for table in ('species', 'aliases'):
        ncbi.cursor.execute('SELECT * FROM ' + table)
        assert ncbi.cursor.fetchall() == []

    mocked_fetch.return_value = (None, None, None)
    assert ncbi.get_species_name('a species') is None
    for table in ('species', 'aliases'):
        ncbi.cursor.execute('SELECT * FROM ' + table)
        assert ncbi.cursor.fetchall() == []

    reset_cache()
    mocked_fetch.return_value = ('1337', 'Scientific name', 'a species')
    assert ncbi.get_species_name('a species') == 'Scientific name'
    assert ncbi.fetch_from_cache('a species') == ('a species', '1337', 'Scientific name', 'a species')
    reset_cache()
