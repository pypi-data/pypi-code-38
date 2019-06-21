import os
import json
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter, QPixmap


class Sprite:
    def __init__(self):
        self._sprite_images = []
        self._width_threshold = 1024

    def _output_width(self, pixmaps):
        """
        Find the output image width
        """
        total_width = sum(
            [pixmap.width for pixmap in pixmaps]
        )
        if total_width > self._width_threshold:
            total_width = self._width_threshold
        return total_width

    def _output_height(self, pixmaps):
        """
        Find the output image height
        """
        total_height = 0
        row_width = 0
        row = []
        for index, pixmap in enumerate(pixmaps):
            if index == 0:
                total_height += pixmap.height
            row.append(pixmap)
            row_width = sum([i.width for i in row])
            if row_width > self._width_threshold:
                total_height += pixmap.height
                row = []
                row.append(pixmap)
        return total_height

    def _save(self, qpixmap, out_json, path, name, scale):
        """
        This method save the sprite image and the corresponding JSON to file
        """
        if scale != 1:
            name = "{}@{}x".format(name, scale)

        qpixmap.save(os.path.join(path, name + '.png'))
        with open(os.path.join(path, name + '.json'), 'w') as outfile:
            json.dump(out_json, outfile)

    def set_width_threshold(self, width):
        self._width_threshold = width

    def add_image(self, sprite_image):
        """
        This method adds a SpriteImage object into the Sprite object
        """
        self._sprite_images.append(sprite_image)

    def has_images(self):
        """Does the sprite have images?"""

        return len(self._sprite_images) > 0

    def render(self, path, scale=1, name='sprite'):
        """
        This method takes all the SpriteImages and render a Sprite and create
        a corresponding JSON file.  The result will be saved to self.sprite,
        and self.json
        """
        pixmaps = []
        for image in self._sprite_images:
            pixmaps.append(image.render(scale))
        pixmaps.sort(reverse=True)
        painter = QPainter()
        device = QPixmap(self._output_width(pixmaps),
                         self._output_height(pixmaps))
        device.fill(Qt.transparent)

        painter.begin(device)
        x = 0
        y = 0
        sprite_json = {}
        row_width = 0
        row_height = pixmaps[0].height
        for index, pixmap in enumerate(pixmaps):
            row_width += pixmap.width
            if row_width > self._width_threshold:
                row_width = pixmap.width
                x = 0
                y += row_height
                row_height = pixmap.height
            source = QRectF(0, 0, pixmap.width, pixmap.height)
            target = QRectF(x, y, pixmap.width, pixmap.height)
            painter.drawPixmap(target, pixmap.qpixmap, source)

            sprite_json[pixmap.id] = {
                "height": pixmap.height,
                "pixelRatio": scale,
                "width": pixmap.width,
                "x": x,
                "y": y
            }

            x += pixmap.width
        painter.end()
        self._save(device, sprite_json, path, name, scale)
