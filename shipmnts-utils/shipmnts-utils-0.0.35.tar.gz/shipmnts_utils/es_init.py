import os

from elasticsearch import Elasticsearch


class ElasticSearch:
    def __init__(self):
        self.client = Elasticsearch(
            [os.getenv("ELASTICSEARCH_HOST", "localhost:9200/")]
        )
