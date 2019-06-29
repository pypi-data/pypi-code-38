from typing import List, Optional
from vortex.Tuple import TupleField, addTupleType, Tuple

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix

@addTupleType
class ImportBranchDeltaColorOverride(Tuple):
    """ Imported Branch Delta Color Override

    This branch delta will change the color of disps.

    """
    __tupleType__ = diagramTuplePrefix + 'ImportBranchDeltaColorOverride'

    #:  A list of keys to apply this color to.
    dispKeys: List[str] = TupleField([])

    #:  The Line Color apples to shape lines
    lineColorHash: Optional[str] = TupleField()

    #:  The Fill Color applies to closed shapes
    fillColorHash: Optional[str] = TupleField()

    #:  This color applies to texts
    colorHash: Optional[str] = TupleField()
