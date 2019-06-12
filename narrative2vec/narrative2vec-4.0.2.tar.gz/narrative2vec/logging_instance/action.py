from narrative2vec.logging_instance.logging_instance import LoggingInstance, _get_first_rdf_query_result
from narrative2vec.ontology.neemNarrativeDefinitions import \
    TASK_SUCCESS, PREVIOUS_ACTION, NEXT_ACTION, SUB_ACTION, \
    OBJECT_ACTED_ON, BODY_PARTS_USED, OBJECT_TYPE, GRASP, FAILURE, ARM, EQUATE, EFFORT

from narrative2vec.ontology.ontologyHandler import get_suffix_of_uri, get_uri


class Action(LoggingInstance):
    def __init__(self, uri, graph):
        super(Action, self).__init__(uri, graph)
        self._equated_action = self.get_equated_action()

    def get_parent_action(self):
        action_property = self._graph_.subjects(get_uri(SUB_ACTION), self.uri)
        parent_uri = _get_first_rdf_query_result(action_property)

        return self._turn_uri_into_action(parent_uri)

    def get_next_action(self):
        return self._get_sibling_action_(NEXT_ACTION)

    def get_previous_action(self):
        return self._get_sibling_action_(PREVIOUS_ACTION)

    def get_object_acted_on(self):
        object_acted_on = self._get_property_(OBJECT_ACTED_ON)

        if object_acted_on:
            object_acted_on = object_acted_on.split('/')[-1]
        elif self._equated_action:
            object_acted_on = self._equated_action.get_object_acted_on()

        return object_acted_on

    def get_object_type(self):
        object_type = self._get_property_(OBJECT_TYPE)

        if object_type:
            object_type = object_type.split('/')[-1]
        elif self._equated_action:
            object_type = self._equated_action.get_object_type()

        return object_type

    def get_grasp(self):
        grasp = self._get_property_(GRASP)

        if grasp and str(grasp) != 'NIL':
            grasp = grasp.split(':')[1]
        elif self._equated_action:
            grasp = self._equated_action.get_grasp()

        return grasp

    def get_body_parts_used(self):
        body_parts_used = self._get_property_(BODY_PARTS_USED)

        if body_parts_used:
            return get_suffix_of_uri(body_parts_used)
        elif self._equated_action:
            body_parts_used = self._equated_action.get_body_parts_used()

        return body_parts_used

    def get_arm(self):
        arm = self._get_property_(ARM)
        if arm:
            return get_suffix_of_uri(arm)
        elif self._equated_action:
            return self._equated_action.get_arm()

    def get_failure(self):
        failure = self._get_property_(FAILURE)

        return failure

    def get_effort(self):
        effort = self._get_property_(EFFORT)

        if not effort and self._equated_action:
            return self._equated_action.get_effort()

        return effort

    def _get_sibling_action_(self, sibling_type):
        sibling_uri = self._get_property_(sibling_type)
        return self._turn_uri_into_action(sibling_uri)

    def _turn_uri_into_action(self, action_uri):
        if action_uri:
            return Action(action_uri, self._graph_)
        return None

    def is_successful(self):
        value = self._get_property_(TASK_SUCCESS)

        return str(value) == 'true'

    def get_type(self):
        # http://knowrob.org/kb/knowrob.owl#PuttingDownAnObject_HLOUBZDW
        return get_suffix_of_uri(self.uri).split('_')[0]

    def get_equated_action(self):
        equated_designator = self._get_property_(EQUATE)
        if equated_designator:
            return Action(equated_designator, self._graph_)

        return None

    # def get_additional_parameters_from_equated_designator(self):
    #     equated_designator = self._get_property_(EQUATE)
    #     additional_parameters = {}
    #
    #     if equated_designator:
    #         equated_designator_predicates = set([x[0] for x in list(self._graph_.predicate_objects(equated_designator))])
    #         action_predicate = set([x[0] for x in list(self._graph_.predicate_objects(self.uri))])
    #         additional_predicates = equated_designator_predicates.difference(action_predicate)
    #         if additional_predicates:
    #             equated_action = Action(equated_designator, self._graph_)
    #             for additional_predicate in additional_predicates:
    #                 predicate_name = get_suffix_of_uri(additional_predicate)
    #                 if predicate_name == ARM:
    #                     additional_parameters[predicate_name] = equated_action.get_arm()
    #                 elif predicate_name == EFFORT:
    #                     additional_parameters[predicate_name] = equated_action.get_arm()
    #                 elif predicate_name == OBJECT_TYPE:
    #                     print 'OBJECT_TYPE'
    #                 elif predicate_name == GRASP:
    #                     print 'GRASP'
    #
    #             print " "
    #         return equated_designator_predicates
    #
    #     return additional_parameters
