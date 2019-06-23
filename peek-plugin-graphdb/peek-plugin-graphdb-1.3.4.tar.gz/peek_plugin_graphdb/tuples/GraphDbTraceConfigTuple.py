import hashlib
from typing import List

from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb.tuples.GraphDbTraceConfigRuleTuple import \
    GraphDbTraceConfigRuleTuple


@addTupleType
class GraphDbTraceConfigTuple(Tuple):
    """ TraceConfig Tuple

    This tuple is the publicly exposed TraceConfig

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbTraceConfigTuple'

    #:  The model set of this segment [Required]
    modelSetKey: str = TupleField()

    #:  The unique key of this trace config [Required]
    key: str = TupleField()

    #:  The name for this trace config [Required]
    name: str = TupleField()

    #:  The title to be displayed to the user [Required]
    title: str = TupleField()

    #:  The name for this trace config
    rules: List[GraphDbTraceConfigRuleTuple] = TupleField([])

    #:  The comment for this trace config
    comment: str = TupleField()

    #:  Is this rule enabled [Required]
    isEnabled: bool = TupleField(True)

    def generateChangedHash(self) -> str:
        rulesStr = [str(rule) for rule in self.rules]
        rulesStr.sort()

        m = hashlib.md5()
        m.update(str(self).encode())
        for ruleStr in rulesStr:
            m.update(ruleStr.encode())

        return m.hexdigest()
