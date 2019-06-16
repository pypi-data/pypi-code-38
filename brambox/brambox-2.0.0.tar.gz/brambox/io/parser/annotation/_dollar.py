#
#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#   Author: Tanguy Ophoff
#
"""
dollar
------
"""
import logging
import numpy as np
from ._base import *

__all__ = ["DollarParser"]
log = logging.getLogger(__name__)


class DollarParser(AnnotationParser):
    """ This parser is designed to parse the version3 text based dollar annotation format from `Piotr Dollar's MATLAB toolbox <toolbox>`_.

    Args:
        precision (integer, optional): The number of decimals for the coordinates; Default **None** (save as int)
        occluded_from_visible (boolean, optional): Whether to compute the occluded percentage from the visible bounding box; Default **False**
        occluded_tag_map (list, optional): When the occluded flag in the dollar text file (see below) is used as an occlusion level tag, \
        its value is used as an index on this list to obtain an occluded fraction that will be stored in the ``occluded`` attribute.

    The dollar format has one .txt file for every image of the dataset where each line within a file represents a bounding box.
    Each line is a space separated list of values structured as follows:

        <label> <x> <y> <w> <h> <occluded> <vx> <vy> <vw> <vh> <ignore> <angle>

    ========  ===========
    Name      Description
    ========  ===========
    label     class label name (string)
    x         left top x coordinate of the bounding box in pixels (integer)
    y         left top y coordinate of the bounding box in pixels (integer)
    w         width of the bounding box in pixels (integer)
    h         height of the bounding box in pixels (integer)
    occluded  1 indicating the object is occluded, 0 indicating the object is not occluded
    vx        left top x coordinate of the inner bounding box that frames the non-occluded part of the object (the visible part)
    vy        left top y coordinate of the inner bounding box that frames the non-occluded part of the object (the visible part)
    vw        width of the inner bounding box that frames the non-occluded part of the object (the visible part)
    vh        height of the inner bounding box that frames the non-occluded part of the object (the visible part)
    ignore    1 indicating the object is ignored, 0 indicating the object is not ignored (mostly 0)
    angle     [0-360] degrees orientation of the bounding box (currently not used)
    ========  ===========

    Example:
        >>> image_000.txt
            % bbGt version=3
            person 488 232 34 100 0 0 0 0 0 0 0
            person 576 219 27 68 0 0 0 0 0 0 0

    Note:
        The ``occluded_from_visible`` argument is only applicable for the deserialization process. |br|
        Due to how brambox stores occlusion as a percentage, we are not able to save the visible box coordinates
        and can thus not regain them when serializing.

    Warning:
        The arguments ``occluded_from_visible`` and ``occluded_tag_map`` are mutually exclusive.
        If you provide both, the parser will generate an error.

    .. _toolbox: https://github.com/pdollar/toolbox/blob/master/detector/bbGt.m
    """
    parser_type = ParserType.MULTI_FILE
    extension = '.txt'
    header = '% bbGt version=3\n'

    def __init__(self, precision=None, occluded_from_visible=False, occluded_tag_map=None):
        super().__init__()

        self.precision = precision
        self.occluded_from_visible = occluded_from_visible
        self.occluded_tag_map = occluded_tag_map

        if self.occluded_from_visible and self.occluded_tag_map is not None:
            raise ValueError('Cannot work with both `occluded_from_visible` and `occluded_tag_map` arguments.')
        elif self.occluded_from_visible:
            log.debug('Computing occluded percentage from visible bounding box area for deserialization.')
        elif self.occluded_tag_map is not None:
            log.debug('Matching occluded value to index of the occluded tag map.')
        else:
            log.debug('Considering occluded value as a binary label.')

    def serialize(self, df):
        result = ''

        for row in df.itertuples():
            label = row.class_label if row.class_label != "" else "?"
            occluded = int(row.occluded > 0) if self.occluded_tag_map is None else self.occluded_tag_map.index(row.occluded)
            lost = int(row.lost)
            result += f'{label} {round(row.x_top_left, self.precision)} {round(row.y_top_left, self.precision)} {round(row.width, self.precision)} {round(row.height, self.precision)} {occluded} 0 0 0 0 {lost} 0\n'

        return result

    def deserialize(self, rawdata, file_id=None):
        self.append_image(file_id)

        for line in rawdata.splitlines():
            if '%' in line:     # ignore comment lines
                continue

            elements = line.split()

            if self.occluded_from_visible:
                occluded = (float(elements[8]) * float(elements[9])) / (float(elements[3]) * float(elements[4])) if float(elements[5]) else 0.0
            elif self.occluded_tag_map is not None:
                occluded = self.occluded_tag_map[int(elements[5])]
            else:
                occluded = float(elements[5])

            self.append(
                file_id,
                elements[0] if elements[0] != '?' else '',
                float(elements[1]),
                float(elements[2]),
                float(elements[3]),
                float(elements[4]),
                occluded=occluded,
                lost=elements[10] != '0'
            )
