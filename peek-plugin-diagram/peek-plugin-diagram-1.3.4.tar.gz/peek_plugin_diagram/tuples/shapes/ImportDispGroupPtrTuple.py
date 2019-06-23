from geoalchemy2 import WKBElement
from typing import List, Optional
from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram.tuples.model.ImportLiveDbDispLinkTuple import \
    ImportLiveDbDispLinkTuple


@addTupleType
class ImportDispGroupPtrTuple(Tuple):
    """ Imported Display Text

    This tuple is used by other plugins to load TEXT objects into the diagram.

    """
    __tupleType__ = diagramTuplePrefix + 'ImportDispGroupPtrTuple'

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
    # If the level shows at all zoom levels, then filtering will move on to the
    # individual disp level.
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

    #: The rotation of the text
    rotation: float = TupleField()

    #: Vertical Stretch, The scale to stretch the display group horizontally
    verticalScale: float = TupleField(1)

    #: Horizontal Stretch, The scale to stretch the display group vertically
    horizontalScale: float = TupleField(1)

    #: Disp Group Hash, The value of a "ImportDispGroupTuple.importHash" to point to
    # This can be null if only an instance (GroupPtr) is imported with no template (Group)
    targetDispGroupHash: Optional[str] = TupleField()

    #: The name of the template that this group pointer was created from.
    targetDispGroupName: Optional[str] = TupleField()

    #: The center location of this
    geom: WKBElement = TupleField()
