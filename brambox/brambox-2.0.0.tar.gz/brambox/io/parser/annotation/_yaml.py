#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
"""
yaml
----
"""
import logging
import yaml
import numpy as np
from ._base import *

__all__ = ["YamlParser"]
log = logging.getLogger(__name__)


class YamlParser(AnnotationParser):
    """
    This parser generates a lightweight human readable annotation format.
    With only one file for the entire dataset, this format will save you precious HDD space and will also be parsed faster.

    Keyword Args:
        keep_ignore (boolean): Whether are not you want to save/load the ignore value; Default **False**
        precision (integer): The number of decimals for the coordinates; Default **None** (save as int)

    Example:
        >>> annotations.yaml
            img1:
              car:
                - coords: [x,y,w,h]
                  lost: False
                  difficult: True
                  occluded_fraction: 50.123
                  truncated_fraction: 0.0
              person:
                - id: 1
                  coords: [x,y,w,h]
                  lost: False
                  difficult: False
                  occluded_fraction: 0.0
                  truncated_fraction: 10.0
                - id: 2
                  coords: [x,y,w,h]
                  lost: False
                  difficult: False
                  occluded_fraction: 0.0
                  truncated_fraction: 0.0
            img2:
              car:
                - coords: [x,y,w,h]
                  lost: True
                  difficult: False
                  occluded_fraction: 90.0
                  truncated_fraction: 76.0
    """
    parser_type = ParserType.SINGLE_FILE
    extension = '.yaml'

    def __init__(self, keep_ignore=False, precision=None):
        super().__init__()
        self.keep_ignore = keep_ignore
        self.precision = precision

    def serialize(self, df):
        result = {}

        for row in df.itertuples():
            box = {
                'coords': [round(row.x_top_left, self.precision), round(row.y_top_left, self.precision),
                           round(row.width, self.precision), round(row.height, self.precision)],
                'lost': row.lost,
                'difficult': row.difficult,
                'occluded_fraction': row.occluded*100,
                'truncated_fraction': row.truncated*100,
            }
            if not np.isnan(row.id):
                box['id'] = int(row.id)
            if self.keep_ignore:
                box['ignore'] = row.ignore

            class_label = row.class_label if row.class_label != '' else '?'
            if class_label not in result:
                result[class_label] = [box]
            else:
                result[class_label].append(box)

        return yaml.dump({df.name: result}, default_flow_style=None)

    def deserialize(self, rawdata, file_id=None):
        yml_obj = yaml.safe_load(rawdata)

        for file_id in yml_obj:
            self.append_image(file_id)
            if yml_obj[file_id] is not None:
                for class_label, annos in yml_obj[file_id].items():
                    class_label = '' if class_label == '?' else class_label
                    for anno in annos:
                        self.append(
                            file_id,
                            class_label,
                            float(anno['coords'][0]),
                            float(anno['coords'][1]),
                            float(anno['coords'][2]),
                            float(anno['coords'][3]),
                            id=anno['id'] if 'id' in anno else None,
                            occluded=anno['occluded_fraction'] / 100,
                            truncated=anno['truncated_fraction'] / 100,
                            lost=anno['lost'],
                            difficult=anno['difficult'],
                            ignore=anno['ignore'] if 'ignore' in anno and self.keep_ignore else False
                        )
