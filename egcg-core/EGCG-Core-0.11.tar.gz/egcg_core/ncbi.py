import re
import sqlite3
import requests
from egcg_core.config import cfg
from egcg_core.app_logging import logging_default as log_cfg

app_logger = log_cfg.get_logger(__name__)

data_cache = None
cursor = None


def _connect():
    global data_cache
    global cursor

    data_cache = sqlite3.connect(cfg['ncbi_cache'])
    cursor = data_cache.cursor()


def _create_tables():
    _create = 'CREATE TABLE IF NOT EXISTS '
    cursor.execute(_create + 'species (taxid text UNIQUE, scientific_name text UNIQUE, common_name text)')
    cursor.execute(_create + 'aliases (query_name text UNIQUE, taxid text REFERENCES species(taxid))')


def connect():
    if data_cache is None and cursor is None:
        _connect()
        _create_tables()


def get_species_name(query_species):
    local_query = fetch_from_cache(query_species)
    if local_query:
        q, taxid, scientific_name, common_name = local_query
    else:
        taxid, scientific_name, common_name = fetch_from_eutils(query_species)
        if taxid is None:
            return None

        _cache_species(query_species, taxid, scientific_name, common_name)

    return scientific_name


def fetch_from_cache(query_species):
    connect()
    cursor.execute('SELECT * FROM aliases NATURAL JOIN species WHERE query_name=?', (query_species,))
    return cursor.fetchone()


def _cache_species(query_species, taxid, scientific_name, common_name):
    connect()
    cursor.execute('SELECT taxid FROM species WHERE taxid=?', (taxid,))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO species VALUES (?, ?, ?)', (taxid, scientific_name, common_name))
    cursor.execute('INSERT INTO aliases VALUES (?, ?)', (query_species, taxid))
    data_cache.commit()


def fetch_from_eutils(species):
    """
    Query NCBI taxomomy database to get the taxonomy ID, scientific name and common name.
    Documentation available at http://www.ncbi.nlm.nih.gov/books/NBK25499/
    :param str species: A search term for esearch, e.g. Human, Mouse, etc.
    """
    esearch_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    payload = {'db': 'Taxonomy', 'term': species, 'retmode': 'JSON'}
    r = requests.get(esearch_url, params=payload)
    results = r.json()
    taxid_list = results.get('esearchresult').get('idlist')
    all_species_names = []
    for taxid in taxid_list:
        efetch_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
        payload = {'db': 'Taxonomy', 'id': taxid}
        r = requests.get(efetch_url, params=payload)
        match = re.search('<Rank>(.+?)</Rank>', r.text, re.MULTILINE)
        rank = None
        if match:
            rank = match.group(1)
        if rank in ['species', 'subspecies']:
            scientific_name = common_name = None
            match = re.search('<ScientificName>(.+?)</ScientificName>', r.text, re.MULTILINE)
            if match:
                scientific_name = match.group(1)
            match = re.search('<GenbankCommonName>(.+?)</GenbankCommonName>', r.text, re.MULTILINE)
            if not match:
                match = re.search('<CommonName>(.+?)</CommonName>', r.text, re.MULTILINE)
            if match:
                common_name = match.group(1)
            all_species_names.append((taxid, scientific_name, common_name))
    nspecies = len(all_species_names)
    if nspecies != 1:
        app_logger.error('%s taxons found for %s', nspecies, species)
        return None, None, None

    return all_species_names[0]


# backward compatibility
_fetch_from_cache = fetch_from_cache
_fetch_from_eutils = fetch_from_eutils
