import re
from typing import Set, Optional, Pattern

from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbTraceConfigRuleTuple(Tuple):
    """ Import Graph Trace Config Rule

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbTraceConfigRuleTuple'

    #:  The processing order of this rule
    order: int = TupleField()

    #:  What should this rule look for
    applyTo: int = TupleField(1)
    APPLY_TO_VERTEX = 1
    APPLY_TO_EDGE = 2
    APPLY_TO_START_VERTEX = 3

    #:  What action should be taken when this rule is met
    action: int = TupleField(1)
    ACTION_STOP_TRACE = 1
    ACTION_CONTINUE_TRACE = 2
    ACTION_ABORT_TRACE_WITH_MESSAGE = 3

    #: Data to go with actions that require it
    actionData: str = TupleField()

    #: The name of the property to apply the rule to
    propertyName: str = TupleField()

    #:  A comma separated list of property values to match
    propertyValue: str = TupleField()

    #:  The type of value in the property value
    propertyValueType: int = TupleField(1)
    PROP_VAL_TYPE_SIMPLE = 1
    PROP_VAL_TYPE_COMMA_LIST = 2
    PROP_VAL_TYPE_REGEX = 3
    PROP_VAL_TYPE_BITMASK_AND = 4

    #:  The comment for this rule
    comment: str = TupleField()

    #:  Is this rule enabled
    isEnabled: bool = TupleField(True)

    # Prepared property values, these are used for matching the this.
    preparedRegex: Optional[Pattern] = None
    preparedValueSet: Optional[Set[str]] = None

    def prepare(self):

        if self.propertyValueType == self.PROP_VAL_TYPE_COMMA_LIST:
            self.preparedValueSet = set(self.propertyValue.split(','))

        elif self.propertyValueType == self.PROP_VAL_TYPE_REGEX:
            self.preparedRegex = re.compile(self.propertyValue)

    def appliesToStr(self):
        if self.applyTo == self.APPLY_TO_VERTEX: return "Vertex"
        if self.applyTo == self.APPLY_TO_EDGE: return "Edge"
        if self.applyTo == self.APPLY_TO_START_VERTEX: return "Start Vertex"
        raise NotImplementedError()

    def actionToStr(self):
        if self.action == self.ACTION_STOP_TRACE:
            return "Stop:%s" % self.actionData

        if self.action == self.ACTION_CONTINUE_TRACE:
            return "Continue:%s" % self.actionData

        if self.action == self.ACTION_ABORT_TRACE_WITH_MESSAGE:
            return "Abort:%s" % self.actionData

        raise NotImplementedError()

    def propertyValueTypeToStr(self):
        if self.propertyValueType == self.PROP_VAL_TYPE_SIMPLE: return "Simple"
        if self.propertyValueType == self.PROP_VAL_TYPE_COMMA_LIST: return "CSV"
        if self.propertyValueType == self.PROP_VAL_TYPE_REGEX: return "Regexp"
        if self.propertyValueType == self.PROP_VAL_TYPE_BITMASK_AND: return "AND"
        raise NotImplementedError()

    def __repr__(self):
        return str(("Order:%s" % self.order,
                    self.appliesToStr(),
                    self.actionToStr(),
                    "%s:%s:%s" % (self.propertyName,
                                  self.propertyValue,
                                  self.propertyValueTypeToStr())))
