from geoalchemy2 import WKBElement
from typing import Optional, List
from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram.tuples.model.ImportLiveDbDispLinkTuple import \
    ImportLiveDbDispLinkTuple


@addTupleType
class ImportDispTextTuple(Tuple):
    """ Imported Display Text

    This tuple is used by other plugins to load TEXT objects into the diagram.

    """
    __tupleType__ = diagramTuplePrefix + 'ImportDispTextTuple'

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

    #: The unique hash of this display object
    importHash: str = TupleField()

    #: The Z Order of this display object when compared against other objects on
    # same layer and level.
    zOrder: int = TupleField()

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

    textStyleHash: str = TupleField()
    colorHash: Optional[str] = TupleField()

    H_ALLIGN_LEFT = -1
    H_ALLIGN_CENTER = 0
    H_ALLIGN_RIGHT = 1
    horizontalAlign: int = TupleField(H_ALLIGN_CENTER)

    V_ALLIGN_TOP = -1
    V_ALLIGN_CENTER = 0
    V_ALLIGN_BOTTOM = 1
    verticalAlign: int = TupleField(V_ALLIGN_CENTER)

    geom: WKBElement = TupleField()

    #: The rotation of the text
    rotation: float = TupleField()

    #: The value of the text
    text: str = TupleField()

    #: This field stores text with format strings that are used to create the text above.
    textFormat: Optional[str] = TupleField()

    #: Text Height (Optional, defaults to height in TextStyle lookup)
    textHeight: Optional[float] = TupleField()

    #: Text Horizontal Stretch, The scale to stretch the text horizontally
    textHStretch: float = TupleField(1)
