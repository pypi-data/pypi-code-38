"""
Parser for configuration file containing the mapping between species names and 
the queries that make part of the URL of the search in the UNIPROT.
"""


def parse_conf(path, prepend="http://www.uniprot.org/uniprot/?query="):
    """Parse the input file.

    Arguments:
        path (str): Path to the files.
        prepend (str): What is prepended to the url (like most of it).
    Yields:
        tuple : name and full url of the species.
    """
    with open(path, 'r') as f:
        for l in f:
            name, url = l.split()
            url = prepend + url
            yield name, url
