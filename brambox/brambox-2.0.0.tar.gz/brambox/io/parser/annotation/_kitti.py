#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
"""
kitti
-----
"""
import logging
import collections
from ._base import *

__all__ = ["KittiParser"]
log = logging.getLogger(__name__)


class KittiParser(AnnotationParser):
    """ This parser can read and write kitti_ annotation files. |br|
    Some of the values of this dataset are not present in the brambox annotation objects and are thus not used.
    When serializing this format, these values will be set to their default value, as per specification.

    ==================  ================  ===========
    Name                Number of Values  Description
    ==================  ================  ===========
    class_label         1                 Annotation class_label. In the official dataset this can be one of: |br|
                                          'Car', 'Van', 'Truck', 'Pedestrian', 'Person_sitting', 'Cyclist', 'Tram', 'Misc' or 'DontCare'

    truncated_fraction  1                 Float in range [0-1] indicating whether object is truncated

    occluded_state      1                 Integer (0,1,2,3) indicating occlusion state: |br|
                                          0=fully visible, 1=partly occluded, 2=largely occluded, 3=unknown, -1=dontcare areas

    alpha               1                 *[Not used in brambox]* Observation angle of the object

    bbox                4                 2D bounding box of the image, expressed in pixel coordinates

    dimensions          3                 *[Not used in brambox]* 3D object dimensions

    location            3                 *[Not used in brambox]* 3D object location

    rotation_y          1                 *[Not used in brambox]* Rotation around Y-axis in camera coordinates
    ==================  ================  ===========

    Example:
        >>> image_000.txt
            <class_label> <truncated_fraction> <occluded_state> -10 <bbox_left> <bbox_top> <bbox_right> <bbox_bottom> -1 -1 -1 -1000 -1000 -1000 -10
            <class_label> <truncated_fraction> <occluded_state> -10 <bbox_left> <bbox_top> <bbox_right> <bbox_bottom> -1 -1 -1 -1000 -1000 -1000 -10
        >>> image_001.txt
            <class_label> <truncated_fraction> <occluded_state> -10 <bbox_left> <bbox_top> <bbox_right> <bbox_bottom> -1 -1 -1 -1000 -1000 -1000 -10
            <class_label> <truncated_fraction> <occluded_state> -10 <bbox_left> <bbox_top> <bbox_right> <bbox_bottom> -1 -1 -1 -1000 -1000 -1000 -10
            <class_label> <truncated_fraction> <occluded_state> -10 <bbox_left> <bbox_top> <bbox_right> <bbox_bottom> -1 -1 -1 -1000 -1000 -1000 -10

    Note:
        Datasets from this source will have an integer as the `occluded` column which represent the different occlusion states.
        Any other function in brambox that works with the `occluded` column probably expect floating point percentages,
        so if you want to use those, you will have to define your own mapping from states to percentages.

    .. _kitti: https://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=2d
    """
    parser_type = ParserType.MULTI_FILE
    extension = '.txt'

    def pre_serialize(self, df):
        if df.occluded.dtype != int:
            log.error('This format expects integer occluded values representing different states. Serializing with floating point occlusion values in stead. [0=fully visible, 1=partly occluded, 2=largely occlude, 3=unkown, -1=dontcare]')
        return df

    def serialize(self, df):
        result = ''

        for row in df.itertuples():
            label = row.class_label if row.class_label != "" else "?"
            trunc = f'{round(row.truncated, 2):.2f}' if row.truncated >= 0 else f'{int(row.truncated)}'
            result += f'{label} {trunc} {row.occluded} -10 {row.x_top_left:.2f} {row.y_top_left:.2f} {row.x_top_left+row.width:.2f} {row.y_top_left+row.height:.2f} -1 -1 -1 -1000 -1000 -1000 -10\n'

        return result

    def deserialize(self, rawdata, file_id=None):
        self.append_image(file_id)
        for line in rawdata.splitlines():
            elements = line.split()
            self.append(
                file_id,
                elements[0] if elements[0] != '?' else '',
                float(elements[4]),
                float(elements[5]),
                float(elements[6]) - float(elements[4]),
                float(elements[7]) - float(elements[5]),
                occluded=float(elements[2]) if '.' in elements[2] else int(elements[2]),
                truncated=max(float(elements[1]), 0.0),
            )
