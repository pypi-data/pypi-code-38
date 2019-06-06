class QueryBuilder:
    def __init__(self, query_params=None, es_version='1'):
        """
        Creates a query builder

        :param query_params: dict with query parameters
        """
        self.es_version = es_version
        self.query_params = query_params
        self.query = self._build_initial_query_string()
        self.filters = []

    def _build_initial_query_string(self):
        if self.query_params is None or 'query' not in self.query_params or self.query_params['query'] == '':
            return {
                'match_all': {}
            }
        else:
            all_fields = '_all' if self.es_version == '1' else '*'
            return {
                'query_string': {
                    'default_field': all_fields,
                    'query': self.query_params['query']
                }
            }

    def add_named_concept_filters(self, named_filter_concepts):
        """
        Adds named concept filters

        :param named_filter_concepts: dict with named filter concepts which will be mapped as the key as query param and the value as search string
        """
        for concept_key, concept_name in named_filter_concepts.items():
            self.add_concept_filter(concept_key, concept_name=concept_name)

    def add_concept_filters(self, filter_concepts):
        """
        Adds concept filters

        :param filter_concepts: list with filter concepts
        """
        for concept in filter_concepts:
            self.add_concept_filter(concept)

    def add_concept_filter(self, concept, concept_name=None):
        """
        Add a concept filter

        :param concept: concept which will be used as lowercase string in a search term
        :param concept_name: name of the place where there will be searched for
        """
        if concept in self.query_params.keys():
            if not concept_name:
                concept_name = concept
            if isinstance(self.query_params[concept], list):
                if self.es_version == '1':
                    es_filter = {'or': []}
                    for or_filter in self.query_params[concept]:
                        es_filter['or'].append(self._build_concept_term(concept_name, or_filter))
                else:
                    es_filter = {"bool": {"should": []}}
                    for or_filter in self.query_params[concept]:
                        es_filter["bool"]["should"].append(self._build_concept_term(concept_name, or_filter))
            else:
                es_filter = self._build_concept_term(concept_name, self.query_params[concept])
            self.filters.append(es_filter)

    def _build_concept_term(self, concept_name, concept):
        filter_method = 'term' if str(self.es_version) == '1' else 'match'
        return {
            filter_method: {concept_name: str(concept).lower()}
        }

    def build(self):
        """
        Builds the query string, which can be used for a search query

        :return: the query string
        """
        if self.es_version == '1':
            if len(self.filters) > 0:
                return {
                    'filtered': {
                        'query': self.query,
                        'filter': {
                            'and': self.filters
                        }
                    }
                }
            else:
                return self.query
        else:
            query = {
                'bool': {
                    'must': self.query
                }
            }
            if len(self.filters) > 0:
                query["bool"]["filter"] = self.filters
            return query

