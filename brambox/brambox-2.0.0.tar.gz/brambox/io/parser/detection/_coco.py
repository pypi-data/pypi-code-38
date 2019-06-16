#
#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#   Author: Tanguy Ophoff
#
"""
coco
----
"""
import logging
import json
from ._base import *

__all__ = ["CocoParser"]
log = logging.getLogger(__name__)


class CocoParser(DetectionParser):
    """ This detection format parser can parse `MS COCO`_ result files for object bounding box detection.

    Keyword Args:
        class_label_map (list, optional): list of class label strings where the ``category_id`` in the json file \
        is used as an index minus one on this list to get the class labels

    A text file contains multiple detections formated using json.
    The file contains one json list where each element represents one bounding box.
    The fields within the elements are:

    ===========  ===========
    Name         Description
    ===========  ===========
    image_id     identifier of the image (integer)
    category_id  class label index (where 1 is the first class label i.s.o. 0) (integer)
    bbox         json list containing bounding box coordinates [top left x, top left y, width, height] (float values)
    score        confidence score between 0 and 1 (float)
    ===========  ===========

    Example:
        >>> detection_results.json
            [
              {"image_id":0, "category_id":1, "bbox":[501.484039, 209.805313, 28.525848, 50.727005], "score":0.189649},
              {"image_id":1, "category_id":1, "bbox":[526.957703, 219.587631, 25.830444, 55.723373], "score":0.477851}
            ]

    .. _MS COCO: http://cocodataset.org/#format-results
    """
    parser_type = ParserType.SINGLE_FILE
    extension = '.json'
    serialize_group = None
    serialize_group_separator = ',\n'
    header = '[\n'
    footer = '\n]'

    def __init__(self, precision=None, class_label_map=None):
        super().__init__()
        self.precision = precision
        self.class_label_map = class_label_map

    def pre_serialize(self, df):
        try:
            df.image = df.image.astype(int)
        except ValueError:
            log.warning('Could not cast image to int, using categorical codes instead.')
            df.image = df.image.cat.codes

        if self.class_label_map is not None:
            df.class_label = df.class_label.map(dict((v, i+1) for i, v in enumerate(self.class_label_map)))
        else:
            try:
                df.class_label = df.class_label.astype(int)
            except ValueError:
                log.error('No class_label_map given and could not cast class_label to int. Setting all labels to 1.')
                df.class_label = 1

        return df

    def serialize(self, row):
        return '  ' + json.dumps(dict(
            image_id=int(row.image),
            category_id=int(row.class_label),
            bbox=[round(float(row.x_top_left), self.precision), round(float(row.y_top_left), self.precision), round(float(row.width), self.precision), round(float(row.height), self.precision)],
            score=row.confidence
        ))

    def deserialize(self, rawdata, file_id=None):
        json_obj = json.loads(rawdata)

        for json_det in json_obj:
            file_id = json_det['image_id']

            if self.class_label_map is not None:
                class_label = self.class_label_map[json_det['category_id'] - 1]
            else:
                class_label = str(json_det['category_id'])

            self.append(
                file_id,
                class_label,
                float(json_det['bbox'][0]),
                float(json_det['bbox'][1]),
                float(json_det['bbox'][2]),
                float(json_det['bbox'][3]),
                confidence=json_det['score'],
            )
