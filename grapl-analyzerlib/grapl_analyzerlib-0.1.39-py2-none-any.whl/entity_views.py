import json

from typing import Optional, List, TypeVar, Dict, Any, Iterator

import grapl_analyzerlib.entity_queries as queries


from pydgraph import DgraphClient

# TODO: Replace DgraphClient with AnalyzerClient
#       We can then parameterize over that, and have an EngagementClient
#       which will allow for merging the libraries
from grapl_analyzerlib import graph_description_pb2



