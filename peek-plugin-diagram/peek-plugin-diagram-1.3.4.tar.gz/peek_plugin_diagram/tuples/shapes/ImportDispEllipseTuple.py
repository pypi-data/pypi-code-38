from geoalchemy2 import WKBElement
from typing import Optional, List
from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram.tuples.model.ImportLiveDbDispLinkTuple import \
    ImportLiveDbDispLinkTuple


@addTupleType
class ImportDispEllipseTuple(Tuple):
    """ Imported Display Ellipse

    This tuple is used by other plugins to load colours into the diagram.

    """
    __tupleType__ = diagramTuplePrefix + 'ImportDispEllipseTuple'

    ### BEGIN DISP COMMON FIELDS ###

    #: Key, This value is a unique ID of the object that this graphic represents
    # It's used to link this graphical object to objects in other plugins, like vertices
    # in the peek-plugin-graphdb plugin.
    # Length = 50
    key: str = TupleField()

    #: Selectable, Is is this item selectable?, the layer also needs selectable=true
    selectable: bool = TupleField()

    #: Data, Generic data, this is passed to the popup context in the UI.
    # peek_plugin_diagram doesn't care as long as it's json compatible or None
    # Json length Length = 400
    data: Optional[dict] = TupleField(None)

    #: The hash of the level to link to (Matches ImportDispLevel.importHash)
    levelHash: str = TupleField()

    #: The hash of the layer to link to (Matches ImportDispLayer.importHash)
    layerHash: str = TupleField()

    #: The Z Order of this display object when compared against other objects on
    # same layer and level.
    zOrder: int = TupleField()

    #: The unique hash of this display object
    importHash: str = TupleField()

    #: The unique hash for all the display items imported in a group with this one.
    #: for example, a page or tile reference.
    importGroupHash: str = TupleField()

    #: The key of the ModelSet to import into
    modelSetKey: str = TupleField()

    #: The Key of the Coordinate Set to import into
    coordSetKey: str = TupleField()

    #: Related links to LiveDB values for this display item
    liveDbDispLinks: List[ImportLiveDbDispLinkTuple] = TupleField()

    #: Parent DispGroup Hash, If this disp is part of a disp group then set this field to
    # the ImportDispGroupTuple.importHash fields value
    # NOTE: If this disp is part of a display group, then the GEOM coordinates need to
    # be relative to 0x0.
    # NOTE: Disps that are apart of a group must all be imported with the same
    # importGroupHash, during the same import call.
    parentDispGroupHash: str = TupleField()

    ### BEGIN FIELDS FOR THIS DISP ###

    lineWidth: int = TupleField()
    lineStyleHash: str = TupleField()
    lineColorHash: Optional[str] = TupleField()
    fillColorHash: Optional[str] = TupleField()

    geom: WKBElement = TupleField()

    xRadius: float = TupleField()
    yRadius: float = TupleField()

    # NOTE, start degree is y=0, x= positive axis (middle right)
    # PEEK draws clockwise from there,
    startAngle: int = TupleField(0)
    endAngle: int = TupleField(360)
