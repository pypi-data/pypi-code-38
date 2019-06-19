""" 
 * orm.Display.py
 *
 *  Copyright Synerty Pty Ltd 2011
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""
import typing

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from sqlalchemy import Column, orm
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm.mapper import reconstructor
from sqlalchemy.sql.schema import Index, Sequence
from sqlalchemy.sql.sqltypes import Float, DateTime
from vortex.Tuple import Tuple, addTupleType, TupleField, JSON_EXCLUDE

from .DeclarativeBase import DeclarativeBase
from .ModelSet import ModelCoordSet, ModelSet

DISP_SHORT_ATTR_NAME_MAP = {'colorId': 'c',
                            'fillColorId': 'fc',
                            'lineColorId': 'lc',
                            'lineStyleId': 'ls',
                            'lineWidth': 'w',
                            'text': 'te',
                            'groupId': 'gi',
                            'targetGroupId': 'tg',
                            }


@addTupleType
class DispLayer(Tuple, DeclarativeBase):
    __tablename__ = 'DispLayer'
    __tupleTypeShort__ = 'DLA'
    __tupleType__ = diagramTuplePrefix + __tablename__

    #: Misc data holder
    data = TupleField()

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    order = Column(Integer, nullable=False, server_default='0')
    selectable = Column(Boolean, nullable=False, server_default='false')
    visible = Column(Boolean, nullable=False, server_default='true')

    modelSetId = Column(Integer, ForeignKey('ModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(ModelSet)

    importHash = Column(String(100), doc=JSON_EXCLUDE)

    __table_args__: typing.Tuple = (
        Index("idx_DispLayer_modelSetId", modelSetId, unique=False),
        Index("idx_DispLayer_importHash", modelSetId, importHash, unique=True),
    )


@addTupleType
class DispLevel(Tuple, DeclarativeBase):
    __tablename__ = 'DispLevel'
    __tupleTypeShort__ = 'DLE'
    __tupleType__ = diagramTuplePrefix + __tablename__

    #: Misc data holder
    data = TupleField()

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    order = Column(Integer, nullable=False, server_default='0')
    minZoom = Column(Float)
    maxZoom = Column(Float)

    coordSetId = Column(Integer,
                        ForeignKey('ModelCoordSet.id', ondelete='CASCADE'),
                        nullable=False)
    coordSet = relationship(ModelCoordSet, foreign_keys=[coordSetId])

    importHash = Column(String(100), doc=JSON_EXCLUDE)

    __table_args__ = (
        Index("idx_DispLevel_coordSetId", coordSetId, unique=False),
        Index("idx_DispLevel_importHash", coordSetId, importHash, unique=True),
    )


@addTupleType
class DispTextStyle(Tuple, DeclarativeBase):
    __tupleTypeShort__ = 'DTS'
    __tablename__ = 'DispTextStyle'
    __tupleType__ = diagramTuplePrefix + __tablename__

    #: Misc data holder
    data = TupleField()

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    fontName = Column(String(30), nullable=False, server_default="GillSans")
    fontSize = Column(Integer, nullable=False, server_default='9')
    fontStyle = Column(String(30))
    scalable = Column(Boolean, nullable=False, server_default="true")
    scaleFactor = Column(Integer, nullable=False, server_default="1")

    modelSetId = Column(Integer, ForeignKey('ModelSet.id', ondelete='CASCADE'),
                        doc=JSON_EXCLUDE, nullable=False)
    modelSet = relationship(ModelSet)

    importHash = Column(String(100), doc=JSON_EXCLUDE)

    __table_args__ = (
        Index("idx_DispTextStyle_modelSetId", modelSetId, unique=False),
        Index("idx_DispTextStyle_importHash", modelSetId, importHash, unique=True),
    )


@addTupleType
class DispLineStyle(Tuple, DeclarativeBase):
    __tupleTypeShort__ = 'DLS'
    __tablename__ = 'DispLineStyle'
    __tupleType__ = diagramTuplePrefix + __tablename__

    #: Misc data holder
    data = TupleField()

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    backgroundFillDashSpace = Column(Boolean, nullable=False, server_default='false')
    capStyle = Column(String(15), nullable=False)
    joinStyle = Column(String(15), nullable=False)
    dashPattern = Column(String(50))
    startArrowSize = Column(Integer)
    endArrowSize = Column(Integer)
    winStyle = Column(Integer, nullable=False)

    modelSetId = Column(Integer, ForeignKey('ModelSet.id', ondelete='CASCADE'),
                        doc=JSON_EXCLUDE, nullable=False)
    modelSet = relationship(ModelSet)

    importHash = Column(String(100), doc=JSON_EXCLUDE)

    __table_args__ = (
        Index("idx_DispLineStyle_modelSetId", modelSetId, unique=False),
        Index("idx_DispLineStyle_importHash", modelSetId, importHash, unique=True),
    )


@addTupleType
class DispColor(Tuple, DeclarativeBase):
    __tupleTypeShort__ = 'DC'
    __tablename__ = 'DispColor'
    __tupleType__ = diagramTuplePrefix + __tablename__

    #: Misc data holder
    data = TupleField()

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), doc=JSON_EXCLUDE, nullable=False)
    color = Column(String(20), server_default='orange')
    altColor = Column(String(20))
    swapPeriod = Column(Float)

    modelSetId = Column(Integer, ForeignKey('ModelSet.id', ondelete='CASCADE'),
                        doc=JSON_EXCLUDE, nullable=False)
    modelSet = relationship(ModelSet)

    importHash = Column(String(100), doc=JSON_EXCLUDE)

    __table_args__ = (
        Index("idx_DispColor_modelSetId", modelSetId, unique=False),
        Index("idx_DispColor_importHash", modelSetId, importHash, unique=True),
    )


class DispBase(Tuple, DeclarativeBase):
    __tablename__ = 'DispBase'

    # Types
    # Must align with constants in javascript DispBase class
    GROUP = 10
    GROUP_PTR = 11
    TEXT = 40
    POLYGON = 50
    POLYLINE = 51
    ELLIPSE = 60
    NULL = 70

    id_seq = Sequence('DispBase_id_seq',
                      metadata=DeclarativeBase.metadata,
                      schema=DeclarativeBase.metadata.schema)
    id = Column(Integer, id_seq, server_default=id_seq.next_value(),
                primary_key=True, autoincrement=False)

    type = Column(Integer, doc=JSON_EXCLUDE, nullable=False)

    # ===== START BRANCH

    #: The branch that this Disp belongs to.
    branchId = Column(Integer, ForeignKey('BranchIndex.id', ondelete='CASCADE'),
                      doc='bi')

    #: The stage of the branch that this DISP
    branchStage = Column(Integer, doc='bs')

    #: This is the unique hash of the contents of this disp within this coordSetId.
    hashId = Column(String, doc='hid')

    #: The coordSetId+hashId that this disp replaces (for branches)
    # ForeignKey('DispBase.id', ondelete='SET NULL'),
    replacesHashId = Column(String, doc='rid')

    # ===== END BRANCH

    #: Used for disps that belong to a DispGroup
    groupId = Column(Integer, ForeignKey('DispBase.id', ondelete='CASCADE'),
                     doc='gi')

    coordSetId = Column(Integer, ForeignKey('ModelCoordSet.id', ondelete='CASCADE'),
                        doc=JSON_EXCLUDE,
                        nullable=False)
    coordSet = relationship(ModelCoordSet)

    #: Layer
    layerId = Column(Integer, ForeignKey('DispLayer.id'), doc='la')
    layer = relationship(DispLayer)

    #: Layer
    levelId = Column(Integer, ForeignKey('DispLevel.id'), doc='le')
    level = relationship(DispLevel)

    #: Order
    zOrder = Column(Integer, server_default='0', nullable=False, doc='z')

    # MAX_STR
    dispJson = Column(String, doc=JSON_EXCLUDE)

    #: The location of this Disp EG - [coordSetId, dispId, 0.0, 0.0] = [..., x, y]
    locationJson = Column(String, doc=JSON_EXCLUDE)

    #: Key, This value is a unique ID of the object that this graphic represents
    key = Column(String, doc='k')

    #: Selectable, Is is this item selectable?, the layer also needs selectable=true
    selectable = Column(Boolean, doc='s', nullable=False, server_default='false')

    #: Data, Generic data that is passed in the context for the item select popup
    dataJson = Column(String, doc='d')

    # THIS FIELD IS NOT USED ANYWHERE!!!!
    importUpdateDate = Column(DateTime(True), doc=JSON_EXCLUDE)

    importHash = Column(String, doc=JSON_EXCLUDE)
    importGroupHash = Column(String, doc=JSON_EXCLUDE)

    liveDbLinks = relationship("LiveDbDispLink")

    __mapper_args__ = {'polymorphic_on': type,
                       'with_polymorphic': '*'}

    __table_args__: typing.Tuple = (
        Index("idx_Disp_importGroupHash", importGroupHash, unique=False),
        # Index("idx_Disp_importHash", importHash, unique=True),
        Index("idx_Disp_importUpdateDate", importUpdateDate, unique=False),

        Index("idx_Disp_layerId", layerId, unique=False),
        Index("idx_Disp_levelId", levelId, unique=False),
        Index("idx_Disp_coordSetId_", coordSetId, unique=False),
        Index("idx_Disp_groupId", groupId, unique=False),
        Index("idx_Disp_branchId", branchId, unique=False),
        # Index("idx_Disp_hashId", coordSetId, hashId, unique=True),
        # Index("idx_Disp_replacesHashId", replacesHashId),
    )


@addTupleType
class DispNull(DispBase):
    """ Disp Null

    This display type does not display at all, It's an object that marks the deletion
    of a prior Disp by a branch.

    Disps in branches replace existing disps, thats how the store the change.
    This disp replaces an existing disp with nothing, with the effect of deleting it.

    This disp does have a geometry, which is equivilent to the bounding box of the shape
    it replaces.

    This whole approach allows the branch delete mechanism to slot into the existing
    diagram structures.

    """
    __tablename__ = 'DispNull'
    __tupleTypeShort__ = 'DN'
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.NULL

    __mapper_args__ = {'polymorphic_identity': RENDERABLE_TYPE}

    id = Column(Integer, ForeignKey('DispBase.id', ondelete='CASCADE')
                , primary_key=True, autoincrement=False)

    geomJson = Column(String, nullable=False, doc='g')

    __table_args__: typing.Tuple = (
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass


@addTupleType
class DispText(DispBase):
    __tablename__ = 'DispText'
    __tupleTypeShort__ = 'DT'
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.TEXT

    __mapper_args__ = {'polymorphic_identity': RENDERABLE_TYPE}

    id = Column(Integer, ForeignKey('DispBase.id', ondelete='CASCADE')
                , primary_key=True, autoincrement=False)

    verticalAlign = Column(Integer, doc='va', nullable=False, server_default='-1')
    horizontalAlign = Column(Integer, doc='ha', nullable=False, server_default='0')
    rotation = Column(Float, doc='r', nullable=False, server_default='0')
    text = Column(String, doc='te', nullable=True, server_default="new text label")
    textFormat = Column(String(1000), doc=JSON_EXCLUDE, nullable=True)

    textHeight = Column(Float, doc='th', nullable=True)
    textHStretch = Column(Float, doc='hs', nullable=False, server_default="1")

    geomJson = Column(String, nullable=False, doc='g')

    colorId = Column(Integer, ForeignKey('DispColor.id'), doc='c')
    color = relationship(DispColor)

    textStyleId = Column(Integer, ForeignKey('DispTextStyle.id'),
                         doc='fs', nullable=False)
    textStyle = relationship(DispTextStyle)

    __table_args__: typing.Tuple = (
        Index("idx_DispText_colorId", colorId, unique=False),
        Index("idx_DispText_styleId", textStyleId, unique=False),
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass


@addTupleType
class DispPolygon(DispBase):
    __tablename__ = 'DispPolygon'
    __tupleTypeShort__ = 'DPG'
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.POLYGON
    __mapper_args__ = {'polymorphic_identity': RENDERABLE_TYPE}

    id = Column(Integer, ForeignKey('DispBase.id', ondelete='CASCADE')
                , primary_key=True, autoincrement=False)

    cornerRadius = Column(Float, doc='cr', nullable=False, server_default='0')
    lineWidth = Column(Integer, doc='w', nullable=False, server_default='2')

    geomJson = Column(String, nullable=False, doc='g')

    fillColorId = Column(Integer, ForeignKey('DispColor.id'), doc='fc')
    fillColor = relationship(DispColor, foreign_keys=fillColorId)

    FILL_TOP_TO_BOTTOM = 0
    FILL_BOTTOM_TO_TOP = 1
    FILL_RIGHT_TO_LEFT = 2
    FILL_LEFT_TO_RIGHT = 3
    fillDirection = Column(Integer, doc='fd')
    fillPercent = Column(Float, doc='fp')
    isRectangle = Column(Boolean, doc='r')

    lineColorId = Column(Integer, ForeignKey('DispColor.id'), doc='lc')
    lineColor = relationship(DispColor, foreign_keys=lineColorId)

    lineStyleId = Column(Integer, ForeignKey('DispLineStyle.id'),
                         doc='ls')
    lineStyle = relationship(DispLineStyle)

    __table_args__ = (
        Index("idx_DispPolygon_fillColorId", fillColorId, unique=False),
        Index("idx_DispPolygon_lineColorId", lineColorId, unique=False),
        Index("idx_DispPolygon_lineStyleId", lineStyleId, unique=False),
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass


@addTupleType
class DispPolyline(DispBase):
    __tablename__ = 'DispPolyline'
    __tupleTypeShort__ = 'DPL'
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.POLYLINE
    __mapper_args__ = {'polymorphic_identity': RENDERABLE_TYPE}

    id = Column(Integer, ForeignKey('DispBase.id', ondelete='CASCADE')
                , primary_key=True, autoincrement=False)

    lineWidth = Column(Integer, doc='w', nullable=False, server_default='2')

    geomJson = Column(String, nullable=False, doc='g')

    lineColorId = Column(Integer, ForeignKey('DispColor.id'), doc='lc')
    lineColor = relationship(DispColor, foreign_keys=lineColorId)

    lineStyleId = Column(Integer, ForeignKey('DispLineStyle.id'), doc='ls')
    lineStyle = relationship(DispLineStyle)

    #: Start Key, The key of another disp object,
    # If the start point of this graphic is linked another disp obj
    startKey = Column(String(50), doc='sk')

    #: End Key, The key of another disp object,
    # If the end point of this graphic is linked another disp obj
    endKey = Column(String(50), doc='ek')

    #: Start end type, is this an arrow, etc?
    startEndType = Column(Integer, doc='st')

    #: End End Type, See Start end type
    endEndType = Column(Integer, doc='et')

    __table_args__ = (
        Index("idx_DispPolyline_lineColorId", lineColorId, unique=False),
        Index("idx_DispPolyline_lineStyleId", lineStyleId, unique=False),
        Index("idx_DispPolyline_startKey", startKey, unique=False),
        Index("idx_DispPolyline_endKey", endKey, unique=False),
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass


@addTupleType
class DispEllipse(DispBase):
    __tablename__ = 'DispEllipse'
    __tupleTypeShort__ = 'DE'
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.ELLIPSE
    __mapper_args__ = {'polymorphic_identity': RENDERABLE_TYPE}

    id = Column(Integer, ForeignKey('DispBase.id', ondelete='CASCADE')
                , primary_key=True, autoincrement=False)

    xRadius = Column(Float, doc='xr', nullable=False, server_default='10.0')
    yRadius = Column(Float, doc='yr', nullable=False, server_default='10.0')
    rotation = Column(Float, doc='r', nullable=False, server_default='0')
    startAngle = Column(Float, doc='sa', nullable=False, server_default='0')
    endAngle = Column(Float, doc='ea', nullable=False, server_default='360')
    lineWidth = Column(Integer, doc='w', nullable=False, server_default='2')

    geomJson = Column(String, nullable=False, doc='g')

    fillColorId = Column(Integer, ForeignKey('DispColor.id'), doc='fc')
    fillColor = relationship(DispColor, foreign_keys=fillColorId)

    lineColorId = Column(Integer, ForeignKey('DispColor.id'), doc='lc')
    lineColor = relationship(DispColor, foreign_keys=lineColorId)

    lineStyleId = Column(Integer, ForeignKey('DispLineStyle.id'),
                         doc='ls')
    lineStyle = relationship(DispLineStyle)

    __table_args__ = (
        Index("idx_DispEllipse_fillColorId", fillColorId, unique=False),
        Index("idx_DispEllipse_lineColorId", lineColorId, unique=False),
        Index("idx_DispEllipse_lineStyleId", lineStyleId, unique=False),
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass


@addTupleType
class DispGroup(DispBase):
    __tablename__ = 'DispGroup'
    __tupleTypeShort__ = 'DG'
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.GROUP
    __mapper_args__ = {'polymorphic_identity': RENDERABLE_TYPE}

    id = Column(Integer, ForeignKey('DispBase.id', ondelete='CASCADE')
                , primary_key=True, autoincrement=False)

    # TODO: this needs to be unique WITH the coordSetId
    name = Column(String, doc='n', nullable=False)
    compileAsTemplate = Column(Boolean, doc=JSON_EXCLUDE,
                               nullable=False, server_default='false')

    disps = relationship(DispBase,
                         primaryjoin='DispBase.groupId==DispGroup.id',
                         foreign_keys=[DispBase.groupId],
                         remote_side='DispBase.groupId')

    #: This field stores an array of disps that belong to this group.
    dispsForJson = TupleField(shortName='di')

    @reconstructor
    def __init__(self):
        DispBase.__init__(self)


@addTupleType
class DispGroupPointer(DispBase):
    __tablename__ = 'DispGroupPointer'
    __tupleTypeShort__ = 'DGP'
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.GROUP_PTR
    __mapper_args__ = {'polymorphic_identity': RENDERABLE_TYPE}

    id = Column(Integer, ForeignKey('DispBase.id', ondelete='CASCADE')
                , primary_key=True, autoincrement=False)

    rotation = Column(Integer, doc='r', server_default='0', nullable=False)

    verticalScale = Column(Float, doc='vs', nullable=False, server_default='1.0')
    horizontalScale = Column(Float, doc='hs', nullable=False, server_default='1.0')

    geomJson = Column(String, nullable=False, doc='g')

    targetDispGroupId = Column(Integer, ForeignKey('DispGroup.id', ondelete='SET NULL'),
                               doc='tg')

    targetDispGroupName = Column(String, doc='tn')

    disps = relationship(DispBase,
                         primaryjoin='DispBase.groupId==DispGroupPointer.id',
                         foreign_keys=[DispBase.groupId],
                         remote_side='DispBase.groupId')

    __table_args__ = (
        Index("idxDispGroupPointer_targetDispGroupId", targetDispGroupId, unique=False),
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass
