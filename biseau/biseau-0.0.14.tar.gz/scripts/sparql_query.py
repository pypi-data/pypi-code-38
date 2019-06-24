"""Allow user to edit and run a SPARQL query,
yield atoms sparql_vars/?, with ? the number of variables in the query.

"""


import os
try:
    from SPARQLWrapper import SPARQLWrapper, JSON
except ImportError:
    DISABLED = 'needs python module SPARQLWrapper'


NAME = 'SPARQL query'
TAGS = {'RDF', 'utils'}
INPUTS = {}
OUTPUTS = {'sparql_vars/*'}
DEFAULT_QUERY = 'data/sparql/solar_system.rq'
DEFAULT_ENDPOINT = 'https://query.wikidata.org/sparql'


def run_on(context:str, *,
           query:open=DEFAULT_QUERY, endpoint:str=DEFAULT_ENDPOINT,
           float_as_int:bool=True):
    """
    query -- (file containing) the full SPARQL query
    endpoint -- URL of the endpoint
    float_as_int -- convert float to integer by rounding them
    """
    if query and os.path.exists(query):
        with open(query) as fd:
            query = fd.read()
    yield from _atoms_from_query(endpoint, query, float_as_int=float_as_int)


def _atoms_from_query(endpoint, query, atom_name:str='sparql_vars', float_as_int:bool=False):
    """Wait for a valid database URI, and a SPARQL query.
    Yields all triplets returned by the query.
    The query need to yield three values, named object, relation and subject.
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
    results = results.convert()
    variables = results['head']['vars']
    for result in results['results']['bindings']:
        yield '{}({}).\n'.format(atom_name, ','.join(_json_to_nuplet(result, variables, float_as_int=float_as_int)))


def _json_to_nuplet(json:dict, variables:tuple, float_as_int:bool=False) -> str:
    """Yield ASP arguments, created by parsing given json dict.

    Expected json object should be as {nuplet component: {'value': value}}.

    """
    values = {}  # variable: ASP value
    for variable in variables:
        yield _aspify_item(json[variable]['value'], float_as_int=float_as_int)


def _aspify_item(item, prefix='"', suffix='"', escapable_chars:str=set('"\\\''),
                 unwanted_chars=set('\n\r'), float_as_int:bool=False) -> str:
    """Return item, human readable"""
    if item.isnumeric() and int(item):
        return item
    elif float_as_int and item.count('.') == 1 and item.replace('.', '').isnumeric():
        return str(round(float(item)))
    else:  # it's a float, or a string
        return prefix + ''.join(
            ('\\' + c) if c in escapable_chars else c
            for c in item
            if c not in unwanted_chars
        ) + suffix
