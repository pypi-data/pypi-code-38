import logging
from typing import Dict

from peek_plugin_diagram._private.storage.Display import DispTextStyle, DispLineStyle, \
    DispColor, DispLevel, DispLayer
from peek_plugin_livedb.tuples.ImportLiveDbItemTuple import ImportLiveDbItemTuple
from sqlalchemy import select

logger = logging.getLogger(__name__)

textTable = DispTextStyle.__table__
lineTable = DispLineStyle.__table__
colorTable = DispColor.__table__
levelTable = DispLevel.__table__
layerTable = DispLayer.__table__


class LiveDbDisplayValueConverter:
    _colorIdByImportHash = None
    _lineStyleIdByImportHash = None

    @staticmethod
    def create(ormSession, modelSetId: int) -> "LiveDbDisplayValueConverter":
        self = LiveDbDisplayValueConverter()

        # self._textStyleIdByImportHash = self._loadLookupByModelSet(
        #     ormSessionCreator, modelSetId, textTable
        # )

        self._lineStyleIdByImportHash = self._loadLookupByModelSet(
            ormSession, modelSetId, lineTable
        )

        self._colorIdByImportHash = self._loadLookupByModelSet(
            ormSession, modelSetId, colorTable
        )

        # self._layerByImportHash = self._loadLookupByModelSet(
        #     ormSessionCreator, modelSetId, layerTable
        # )
        #
        return self

    def translate(self, dataType, rawValue):
        return self._liveDbTranslators[dataType](self, rawValue)

    @staticmethod
    def _loadLookupByModelSet(ormSession, modelSetId: int, table) -> Dict[str, int]:
        resultSet = ormSession.execute(
            select([table.c.importHash, table.c.id])
                .where(table.c.modelSetId == modelSetId))

        return dict(resultSet.fetchall())

    def _liveDbValueTranslateColorId(self, value):
        return self._colorIdByImportHash.get(value)

    def _liveDbValueTranslateLineStyleId(self, value):
        return self._lineStyleIdByImportHash.get(value)

    def _liveDbValueTranslateLineWidth(self, value):
        return value

    def _liveDbValueTranslateText(self, value):
        return '' if value is None else value

    def _liveDbValueTranslateNumber(self, value):
        return value

    def _liveDbValueTranslateGroupId(self, value):
        raise NotImplementedError()

    _liveDbTranslators = {
        ImportLiveDbItemTuple.DATA_TYPE_COLOR: _liveDbValueTranslateColorId,
        ImportLiveDbItemTuple.DATA_TYPE_LINE_STYLE: _liveDbValueTranslateLineStyleId,
        ImportLiveDbItemTuple.DATA_TYPE_LINE_WIDTH: _liveDbValueTranslateLineWidth,
        ImportLiveDbItemTuple.DATA_TYPE_STRING_VALUE: _liveDbValueTranslateText,
        ImportLiveDbItemTuple.DATA_TYPE_NUMBER_VALUE: _liveDbValueTranslateNumber,
        ImportLiveDbItemTuple.DATA_TYPE_GROUP_PTR: _liveDbValueTranslateGroupId,
    }
