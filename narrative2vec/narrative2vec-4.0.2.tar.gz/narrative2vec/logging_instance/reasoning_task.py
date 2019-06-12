from narrative2vec.logging_instance.action import Action
from narrative2vec.logging_instance.logging_instance import LoggingInstance, _get_first_rdf_query_result
from narrative2vec.ontology.neemNarrativeDefinitions import PREDICATE
from narrative2vec.ontology.ontologyHandler import get_uri


class ReasoningTask(LoggingInstance):
    def get_parameters(self):
        return _clean_query_result_(self._get_property_('parameter'))

    def get_predicate(self):
        return self._get_property_(PREDICATE)

    def get_result(self):
        return _clean_query_result_(self._get_property_('result'))

    def get_action_id(self):
        action_property = self._graph_.subjects(get_uri('reasoningTask'), self.uri)
        action = _get_first_rdf_query_result(action_property)

        if action and not action.startswith('file://'):
            return Action(action, self._graph_).get_id()

        return ''


def _clean_query_result_(query_result):
    if query_result.startswith('file://'):
        return query_result.split('/')[-1]
    return query_result
