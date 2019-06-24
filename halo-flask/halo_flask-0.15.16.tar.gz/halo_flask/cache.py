from __future__ import print_function

import elasticache_auto_discovery
from pymemcache.client.hash import HashClient

# elasticache settings
elasticache_config_endpoint = "your-elasticache-cluster-endpoint:port"
nodes = elasticache_auto_discovery.discover(elasticache_config_endpoint)
nodes = map(lambda x: (x[1], int(x[2])), nodes)
memcache_client = HashClient(nodes)


def put(requestId, event):
    """
    This function puts into memcache and get from it.
    Memcache is hosted using elasticache
    """

    # Put the UUID to the cache.
    memcache_client.set(requestId, event)


def get(requestId):
    # Get item (UUID) from the cache.
    item = memcache_client.get(requestId)

    return item
