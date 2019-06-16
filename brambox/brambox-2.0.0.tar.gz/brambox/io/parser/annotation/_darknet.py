#
#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#
"""
darknet
-------
"""
import logging
import numpy as np
from ._base import *

__all__ = ["DarknetParser"]
log = logging.getLogger(__name__)


class DarknetParser(AnnotationParser):
    """ This parser is designed to parse the darknet annotation format.

    The format is a multifile format (one file per image). The format uses relative x, y, width, height coordinates where
    x and width are divided by the image width and y and height are divided by the image height. This results in decimal numbers
    between 0 and 1.

    Args:
        image_dims (callable or dict-like object): lambda with as input an image_id which should return a tuple (image_width,
                    image_heigt) or a dict-like object with as key an image_id and as values the same tuple.
        class_label_map (list): list of class labels to translate a label to a class label index (the index in the list) and visa versa
        precision (integer, optional): The max number of decimal digits for the coordinates (between 0 and 1) used when serializing; Default **8**

    Example:
        >>> image_000.txt
            <class_label_index> <x_center> <y_center> <width> <height>
            <class_label_index> <x_center> <y_center> <width> <height>
            <class_label_index> <x_center> <y_center> <width> <height>
        >>> image_001.txt
            <class_label_index> <x_center> <y_center> <width> <height>
    """
    parser_type = ParserType.MULTI_FILE
    extension = '.txt'

    def __init__(self, image_dims=None, class_label_map=None, precision=8):
        super().__init__()

        self.image_dims = image_dims
        if self.image_dims is None:
            raise ValueError('Darknet parser requires image_dims argument')

        self.class_label_map = class_label_map
        if self.class_label_map is None:
            raise ValueError('Darknet parser requires class_label_map argument')

        self.precision = precision

    def serialize(self, df):
        if callable(self.image_dims):
            # assume df is already grouped by 'image'
            image_w, image_h = self.image_dims(df.name)
        else:
            image_w, image_h = self.image_dims[df.name]

        df.x_top_left /= image_w
        df.y_top_left /= image_h
        df.width /= image_w
        df.height /= image_h

        # now serialize in a regular fashion
        result = ''
        for row in df.itertuples():
            class_label_index = self.class_label_map.index(row.class_label)
            x_center = round(row.x_top_left + row.width / 2, self.precision)
            y_center = round(row.y_top_left + row.height / 2, self.precision)
            width = round(row.width, self.precision)
            height = round(row.height, self.precision)
            result += f'{class_label_index} {x_center} {y_center} {width} {height}\n'

        return result

    def deserialize(self, rawdata, file_id=None):
        if callable(self.image_dims):
            image_w, image_h = self.image_dims(file_id)
        else:
            image_w, image_h = self.image_dims[file_id]

        self.append_image(file_id)

        for line in rawdata.splitlines():

            elements = line.split()
            class_label = self.class_label_map[int(elements[0])]
            x_center = float(elements[1]) * image_w
            y_center = float(elements[2]) * image_h
            width = float(elements[3]) * image_w
            height = float(elements[4]) * image_h

            self.append(
                file_id,
                class_label,
                x_center - width / 2,
                y_center - height / 2,
                width,
                height
            )
