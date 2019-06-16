#
#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#   Author: Tanguy Ophoff
#
"""
coco
----
"""
import os
import logging
import json
from ._base import *

__all__ = ["CocoParser"]
log = logging.getLogger(__name__)


class CocoParser(AnnotationParser):
    """
    This parser can parse annotations in the `MS COCO`_ format.
    This format consists of one json file for the whole dataset

    Args:
        add_image_dims (boolean, optional): If True, `image_width` and `image_height` columns are added to the deserialized data frame; Default **False**

    Note:
        The `iscrowd` flag is mapped to the `ignore` flag.

    Warning:
        This parser does not implement a serialization function
        as the COCO format has a lot of extra metadata which is not representable in the brambox data structure.

    .. _MS COCO: http://cocodataset.org/#format-data
    """
    parser_type = ParserType.SINGLE_FILE
    extension = '.json'

    def __init__(self, add_image_dims=False):
        super().__init__()

        self.add_image_dims = add_image_dims
        if self.add_image_dims:
            self.data['image_width'] = []
            self.data['image_height'] = []

    def serialize(self, df):
        raise NotImplementedError('This parser does not allow to save COCO json files, as there is too much different metadata in this format')

    def deserialize(self, rawdata, file_id=None):
        root = json.loads(rawdata)

        # create class label map for mapping class label ids to class label names
        class_label_map = {cat['id']: cat['name'] for cat in root['categories']}

        # create an image name map to map image ids to image names
        # and make sure all images are registered
        image_id_map = {}
        for image in root['images']:
            file_name = os.path.splitext(image['file_name'])[0]
            image_id_map[image['id']] = file_name
            self.append_image(file_name)

        # optionally create image size map to map image ids to image width and height
        if self.add_image_dims:
            image_size_map = {img['id']: (img['width'], img['height']) for img in root['images']}

        # parse bboxes
        for anno in root['annotations']:
            image_id = image_id_map[anno['image_id']]
            class_label = class_label_map[anno['category_id']]
            ignore = anno['iscrowd'] != 0
            obj_id = float(anno['id'])

            bbox = anno['bbox']
            x_top_left = float(bbox[0])
            y_top_left = float(bbox[1])
            width = float(bbox[2])
            height = float(bbox[3])

            self.append(
                image_id,
                class_label,
                x_top_left,
                y_top_left,
                width,
                height,
                id=obj_id,
                ignore=ignore
            )

            # append to custom image_width and image_height cols
            if self.add_image_dims:
                image_size = image_size_map[anno['image_id']]
                self.data['image_width'].append(image_size[0])
                self.data['image_height'].append(image_size[1])
