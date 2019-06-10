from dli.client.entities_mixin import EntityMixin
from dli.client.search_functions import SearchFunctions
from dli.client.me_functions import MeFunctions


"""
Define the client mixin here which consists of the mixin aggregated by 
function groups, for e.g entities, search, user etc.
"""
class ClientMixin(EntityMixin, MeFunctions, SearchFunctions):
    pass