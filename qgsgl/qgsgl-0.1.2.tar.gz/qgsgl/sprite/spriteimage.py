from qgis.core import QgsSymbolLayerUtils, QgsMapSettings, QgsUnitTypes
from PyQt5.QtCore import QSize, QRect, QPoint
from PyQt5.QtGui import qAlpha
from .spritepixmap import SpritePixmap


class SpriteImage:
    def __init__(self, symbol_layer, image_id):
        self.qgis_symbol_layer = symbol_layer
        self._canvas_height = 250
        self._canvas_width = 250
        self.image_id = image_id

    def _get_ratio_factor(self, scale):
        """
        Calculate the ratio of the image based on local setting
        """
        map_setting = QgsMapSettings()
        return scale / map_setting.devicePixelRatio()

    def _bbox(self, pic):
        """
        Find the minimum bounding box for the QImage
        """
        len = pic.width()
        height = pic.height()
        r = 0
        b = 0

        for y in range(pic.height()):
            rowFilled = False
            for x in range(pic.width()):
                if qAlpha(pic.pixel(x, y)):
                    rowFilled = True
                    r = max(r, x)
                    if len > x:
                        len = x
            if rowFilled:
                height = min(height, y)
                b = y
        return QRect(QPoint(len, height), QPoint(r, b))

    def render(self, scale=1):
        """
        Create the QPixmap object from QGIS symbol layer
        """
        clone = self.qgis_symbol_layer.clone()
        clone.setSize(clone.size() * self._get_ratio_factor(scale))

        qicon = QgsSymbolLayerUtils.symbolLayerPreviewIcon(
            clone,
            QgsUnitTypes.RenderPixels,
            QSize(self._canvas_height, self._canvas_height),
            clone.mapUnitScale()
        )
        bbox = self._bbox(
                qicon.pixmap(
                    self._canvas_height, self._canvas_width
                ).toImage()
            )
        qpixmap = qicon.pixmap(
            self._canvas_height, self._canvas_width
        ).copy(bbox)

        return SpritePixmap(qpixmap, self.image_id)
