#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
"""
pascal voc
----------
"""
import logging
import numpy as np
from ._base import *

__all__ = ["PascalVocParser"]
log = logging.getLogger(__name__)


class PascalVocParser(DetectionParser):
    """
    This parser can parse detections in the `pascal voc`_ format.
    This format consists of one file per class of detection. |br|
    confidence_scores are saved as a number between 0-1, coordinates are saved as pixel values.

    Args:
        images (list): List of all the images; Default **None** (infer from data)
        precision (integer): The number of decimals for the coordinates; Default **None** (save as int)

    Example:
        >>> person.txt
            <img_000> <confidence_score> <x_left> <y_upper> <x_right> <y_lower>
            <img_000> <confidence_score> <x_left> <y_upper> <x_right> <y_lower>
            <img_073> <confidence_score> <x_left> <y_upper> <x_right> <y_lower>
        >>> cat.txt
            <img_011> <confidence_score> <x_left> <y_upper> <x_right> <y_lower>

    Note:
        As this format has no way of specifying all the possible images,
        you might want to give that list to this parser through the `images` argument.
        If you do not give such a list, only the images for which there are detections will be added.

    .. _pascal voc: http://host.robots.ox.ac.uk/pascal/VOC/
    """
    parser_type = ParserType.MULTI_FILE
    extension = '.txt'
    serialize_group = 'class_label'

    def __init__(self, images=None, precision=None):
        super().__init__()
        self.precision = precision
        if images is not None:
            [self.append_image(img) for img in images]
        else:
            log.warning("No 'images' given, only images that contain detections will be included in the dataframe (deserialization only)")

    def serialize(self, df):
        result = ''

        for row in df.itertuples():
            result += f'{row.image} {row.confidence} {round(row.x_top_left, self.precision)} {round(row.y_top_left, self.precision)} {round(row.x_top_left+row.width, self.precision)} {round(row.y_top_left+row.height, self.precision)}\n'

        return result

    def deserialize(self, rawdata, file_id=None):
        for line in rawdata.splitlines():
            elements = line.split()
            x = float(elements[2])
            y = float(elements[3])
            w = float(elements[4]) - x
            h = float(elements[5]) - y
            self.append(
                elements[0],
                file_id,
                x, y, w, h,
                confidence=float(elements[1]),
            )
