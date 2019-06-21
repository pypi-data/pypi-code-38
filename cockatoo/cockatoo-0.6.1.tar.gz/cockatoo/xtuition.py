import os
import requests
import cockatoo

base_uri = 'http://xtuition.org/api'

class ApiError(Exception):
    pass

def _auth():
    if 'XTUITION_TOKEN' not in os.environ:
        raise(ValueError('Please set XTUITION_TOKEN environment variable'))
    return {'Authorization': 'Bearer {}'.format(os.environ['XTUITION_TOKEN'])}

def fetch_json(endpoint, payload=None):
    url = base_uri + endpoint
    r = requests.get(url, headers=_auth(), params=payload)
    if r.status_code != 200:
        raise(ApiError('Invalid response code {} for url: {}'.format(r.status_code, r.url)))

    return r

def fetch_screen(id):
    endpoint = '/screen/' + str(id) + '/cockatoo'
    r = fetch_json(endpoint)
    return cockatoo.screen.loads(r.text)

def fetch_cocktail(id):
    endpoint = '/cocktail/' + str(id) + '/cockatoo'
    r = fetch_json(endpoint)
    return cockatoo.screen._parse_cocktail_json(r.json())

def fetch_compound(id):
    endpoint = '/compound/' + str(id)
    r = fetch_json(endpoint)
    cp = r.json()
    compound = cockatoo.screen.Compound(cp['name'], 0, '')
    compound.molecular_weight = cp['molecular_weight']
    compound.smiles = cp['smiles']
    compound.density = cp['density']
    return compound

def fetch_compound_by_name(name):
    endpoint = '/compound/find'
    r = fetch_json(endpoint, payload={'name': name})
    cp = r.json()
    compound = cockatoo.screen.Compound(cp['name'], 0, '')
    compound.molecular_weight = cp['molecular_weight']
    compound.smiles = cp['smiles']
    compound.density = cp['density']
    return compound
