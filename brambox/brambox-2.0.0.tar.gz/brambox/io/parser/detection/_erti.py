#
#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#
"""
erti
----
"""
import logging
import numpy as np
from ._base import *

__all__ = ["ErtiParser"]
log = logging.getLogger(__name__)


class ErtiParser(DetectionParser):
    """
    This parser is designed to parse the detection format of the `ERTI challenge`_

    Keyword Args:
        class_label (string, optional): class label name of the detections (this format only supports single object class detections)

    One text file per image:
    Each line is a comma separated list of values structured as follows:

        <x>,<y>,<width>,<height>,<score>

    =========  ===========
    Name       Description
    =========  ===========
    x          top left x coordinate of the bounding box in pixels (integer)
    y          top left y coordinate of the bounding box in pixels (integer)
    w          width of the bounding box in pixels (integer)
    h          height of the bounding box in pixels (integer)
    score      detection score between 0 and 1 (float)
    =========  ===========

    Example:
        >>> 000.txt
            503.75,213,20.5,50,74.8391

        >>> 001.txt
            540.8,166.4,37.4857,91.4286,56.4761
            519.034,186.602,31.6574,77.2131,51.2428

    .. _ERTI challenge: https://sites.google.com/site/uavision2019/challenge
    """
    parser_type = ParserType.MULTI_FILE
    extension = '.txt'

    def __init__(self, class_label=''):
        super().__init__()
        self.class_label = class_label

    def serialize(self, df):
        result = ''
        if df.class_label.nunique() > 1:
            raise ValueError('This parser is meant for single-class problems and as such does not have the means to store class labels. All objects will be stored as the same class.')

        for row in df.itertuples():
            result += f'{round(row.x_top_left)},{round(row.y_top_left)},{round(row.width)},{round(row.height)},{row.confidence}\n'

        return result

    def deserialize(self, rawdata, file_id=None):
        self.append_image(file_id)
        for line in rawdata.splitlines():
            elements = line.split(',')
            self.append(
                file_id,
                self.class_label,
                float(elements[0]),
                float(elements[1]),
                float(elements[2]),
                float(elements[3]),
                confidence=float(elements[4]),
            )
