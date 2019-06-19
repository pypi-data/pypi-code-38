from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_gis_diagram._private.PluginNames import gisDiagramTuplePrefix


@addTupleType
class GisDiagramTuple(Tuple):
    """ GisDiagram Tuple

    This tuple is a create example of defining classes to work with our data.
    """
    __tupleType__ = gisDiagramTuplePrefix + 'GisDiagramTuple'

    #:  Description of date1
    dict1 = TupleField(defaultValue=dict)

    #:  Description of date1
    array1 = TupleField(defaultValue=list)

    #:  Description of date1
    date1 = TupleField()
