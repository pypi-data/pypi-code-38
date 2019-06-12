from narrative2vec.logging_instance.logging_instance import LoggingInstance, _get_first_rdf_query_result
from narrative2vec.logging_instance.reasoning_task import ReasoningTask
from narrative2vec.ontology.neemNarrativeDefinitions import QUATERNION
from narrative2vec.ontology.ontologyHandler import get_uri


class Pose(LoggingInstance):
    def get_translation(self):
        read_translation = self._get_property_('translation')
        return read_translation.strip().split()

    def get_quaternion(self):
        read_orientation = self._get_property_(QUATERNION)
        return read_orientation.strip().split()

    def get_reasoning_task__id(self):
        reasoning_task_property = self._graph_.subjects(get_uri('parameter2'), self.uri)
        reasoning_task = _get_first_rdf_query_result(reasoning_task_property)

        if reasoning_task and not reasoning_task.startswith('file://'):
            return ReasoningTask(reasoning_task, self._graph_).get_id()

        return ''