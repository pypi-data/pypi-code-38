"""Provides storage utilities"""

import os
def path_from_uuid(uuid_):
    """
    create a filepath from a UUID
    e.g.
    uuid_ = cbb33a87-6754-4dfd-abd3-7466d4463ebc
    will return
    cb/b3/cbb33a87-6754-4dfd-abd3-7466d4463ebc
    """
    uuid_1 = uuid_.split('-')[0]
    first_stanza = uuid_1[0:2]
    second_stanza = uuid_1[2:4]
    path = (first_stanza, second_stanza, uuid_)
    return os.path.join(*path)

def format_hash(hash_alg, hash_):
    """
    format the hash including version and algorithm
    """
    return '-'.join(('v0', hash_alg, hash_))

# Import urllparse from python2/3
try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs

def parse_storage_url(urlstring):
    """Parse the given urllstring.

    Args:
        urlstring (str): The url string to parse

    Returns:
        tuple: A tuple of scheme, bucket_name, path, query
    """
    result = urlparse(urlstring)
    parsed_query = {}
    for key, value in parse_qs(result.query).items():
        if isinstance(value, list) and len(value) == 1:
            value = value[0]
        parsed_query[key] = value
    return result.scheme, result.netloc, result.path, parsed_query
