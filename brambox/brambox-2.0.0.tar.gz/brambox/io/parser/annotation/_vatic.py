#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
"""
vatic
-----
"""
import logging
import numpy as np
from ._base import *

__all__ = ["VaticParser"]
log = logging.getLogger(__name__)


class VaticParser(AnnotationParser):
    """ This parser is designed to parse the standard VATIC_ video annotation tool text files.
    The VATIC format contains all annotation from multiple images into one file.
    Each line of the file represents one bounding box from one image and is a spaces separated
    list of values structured as follows:

        <track_id> <xmin> <ymin> <xmax> <ymax> <frame> <lost> <occluded> <generated> <label>

    =========  ===========
    Name       Description
    =========  ===========
    track_id   identifier of the track this object is following (integer)
    xmin       top left x coordinate of the bounding box (integer)
    ymin       top left y coordinate of the bounding box (integer)
    xmax       bottom right x coordinate of the bounding box (integer)
    ymax       bottom right y coordinate of the bounding box (integer)
    frame      image identifier that this annotation belong to (integer)
    lost       1 if the annotated object is outside of the view screen, 0 otherwise
    occluded   1 if the annotated object is occluded, 0 otherwise
    generated  1 if the annotation was automatically interpolated, 0 otherwise (not used)
    label      class label of the object, enclosed in quotation marks
    =========  ===========

    Example:
        >>> video_000.txt
            1 578 206 762 600 282 0 0 0 "person"
            2 206 286 234 340 0 1 0 0 "person"
            8 206 286 234 340 10 1 0 1 "car"

    Note:
        If there is no id, it is set to **-1** when serializing.

    .. _VATIC: https://github.com/cvondrick/vatic
    """
    parser_type = ParserType.SINGLE_FILE
    extension = '.txt'

    def __init__(self, occluded_cutoff=0.5):
        super().__init__()
        self.occluded_cutoff = occluded_cutoff

    def pre_serialize(self, df):
        try:
            df.image = df.image.astype(int)
        except ValueError:
            log.warning('Could not convert image column to integers, using categorical codes')
            df.image = df.image.cat.codes

        df.x_top_left = df.x_top_left.round().astype(int)
        df.y_top_left = df.y_top_left.round().astype(int)
        df.width = df.width.round().astype(int)
        df.height = df.height.round().astype(int)

        return df

    def serialize(self, df):
        result = ''

        for row in df.itertuples():
            if not np.isnan(row.id):
                idval = int(row.id)
            else:
                idval = -1
            occ = int(row.occluded >= self.occluded_cutoff)
            result += f'{idval} {row.x_top_left} {row.y_top_left} {row.x_top_left + row.width} {row.y_top_left + row.height} {row.image} {int(row.lost)} {occ} 0 "{row.class_label}"\n'

        return result

    def deserialize(self, rawdata, file_id=None):
        for line in rawdata.splitlines():
            elements = line.split()

            idval = float(elements[0])
            if idval < 0:
                idval = None
            x = float(elements[1])
            y = float(elements[2])

            self.append(
                elements[5],
                elements[9][1:-1],
                x,
                y,
                float(elements[3]) - x,
                float(elements[4]) - y,
                id=idval,
                lost=elements[6] == '1',
                occluded=float(elements[7] == '1'),
            )
