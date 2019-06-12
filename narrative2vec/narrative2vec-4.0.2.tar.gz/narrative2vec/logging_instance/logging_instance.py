from narrative2vec.ontology.neemNarrativeDefinitions import START_TIME, END_TIME
from narrative2vec.ontology.ontologyHandler import get_suffix_of_uri, get_uri


def _get_time_from_timepoint(timepoint):
    return float(get_suffix_of_uri(timepoint).split('_')[1])


def _get_first_rdf_query_result(result):
    try:
        return list(result)[0]
    except IndexError:
        return None


class LoggingInstance(object):
    def __init__(self, uri, graph):
        self.uri = uri
        self._graph_ = graph

    def get_id(self):
        return get_suffix_of_uri(self.uri)

    def get_start_time_(self):
        return self._get_time_(START_TIME)

    def get_end_time(self):
        return self._get_time_(END_TIME)

    def _get_time_(self, time_type):
        time = self._get_property_(time_type)

        if time:
            return _get_time_from_timepoint(time)

        return 0.0

    def _get_property_(self, uri_prefix):
        action_property = self._graph_.objects(self.uri, get_uri(uri_prefix))
        return _get_first_rdf_query_result(action_property)