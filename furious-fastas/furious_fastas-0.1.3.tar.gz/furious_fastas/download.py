import requests


def download(url):
    """Download the query/species sequences from Uniprot.

	This is an equivalent of 'wget url', but inside python.

    Arguments
    =========
    url : str
        The url with uniprot query, e.g. 
        http://www.uniprot.org/uniprot/?query=reviewed:yes+AND+organism:9606&format=fasta
        is the one to retrieve all reviewed human proteins.
    """
    return requests.get(url).text