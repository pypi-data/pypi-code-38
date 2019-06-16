#
#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#   Author: Tanguy Ophoff
#
"""
pascal voc
----------
"""
import logging
import numpy as np
import xml.etree.ElementTree as ET
from ._base import *

__all__ = ["PascalVocParser"]
log = logging.getLogger(__name__)


class PascalVocParser(AnnotationParser):
    """
    This parser can parse annotations in the `pascal voc`_ format.
    This format consists of one xml file for every image.

    Args:
        truncated_cutoff (Number, optional): Minimum value to consider an annotation as truncated; Default **0.15**
        occluded_cutoff (Number, optional): Minimum value to consider an annotation as occluded; Default **0.05**

    Example:
        >>> image_000.xml
            <annotation>
              <object>
                <name>horse</name>
                <truncated>1</truncated>
                <difficult>0</difficult>
                <bndbox>
                  <xmin>100</xmin>
                  <ymin>200</ymin>
                  <xmax>300</xmax>
                  <ymax>400</ymax>
                </bndbox>
              </object>
              <object>
                <name>person</name>
                <truncated>0</truncated>
                <difficult>1</difficult>
                <bndbox>
                  <xmin>110</xmin>
                  <ymin>20</ymin>
                  <xmax>200</xmax>
                  <ymax>350</ymax>
                </bndbox>
              </object>
            </annotation>

    Note:
        For serialization, both cutoff values are used in a strictly bigger than comparison to decide whether or not
        the annotations are to be considered truncated/occluded in the boolean values that this format has. |br|
        The default values of 15% for truncation and 5% for occlusion have been taken from the `annotators guidelines <voc guidelines>`_.

        For Deserialization, we convert the boolean values to either 0% or 100%.

    .. _pascal voc: http://host.robots.ox.ac.uk/pascal/VOC/
    .. _voc guidelines: http://host.robots.ox.ac.uk/pascal/VOC/voc2012/guidelines.html
    """
    parser_type = ParserType.MULTI_FILE
    extension = '.xml'

    def __init__(self, truncated_cutoff=0.15, occluded_cutoff=0.05):
        super().__init__()
        self.truncated_cutoff = truncated_cutoff
        self.occluded_cutoff = occluded_cutoff

    def serialize(self, df):
        result = '<annotation>\n'

        for row in df.itertuples():
            string = '<object>\n'
            string += f'\t<name>{row.class_label}</name>\n'
            string += '\t<pose>Unspecified</pose>\n'
            string += f'\t<truncated>{int(row.truncated > self.truncated_cutoff)}</truncated>\n'
            string += f'\t<occluded>{int(row.occluded > self.occluded_cutoff)}</occluded>\n'
            string += f'\t<difficult>{int(row.difficult)}</difficult>\n'
            string += '\t<bndbox>\n'
            string += f'\t\t<xmin>{round(row.x_top_left)}</xmin>\n'
            string += f'\t\t<ymin>{round(row.y_top_left)}</ymin>\n'
            string += f'\t\t<xmax>{round(row.x_top_left + row.width)}</xmax>\n'
            string += f'\t\t<ymax>{round(row.y_top_left + row.height)}</ymax>\n'
            string += '\t</bndbox>\n'
            string += '</object>\n'

            result += string

        return result + '</annotation>\n'

    def deserialize(self, rawdata, file_id=None):
        self.append_image(file_id)

        root = ET.fromstring(rawdata)
        for xml_obj in root.iter('object'):
            class_label = xml_obj.findtext('name', '')
            truncated = float(xml_obj.findtext('truncated', 0))
            occluded = float(xml_obj.findtext('occluded', 0))
            difficult = xml_obj.findtext('difficult', 0) == '1'

            box = xml_obj.find('bndbox')
            x_top_left = float(box.findtext('xmin', 0))
            y_top_left = float(box.findtext('ymin', 0))
            width = float(box.findtext('xmax', 0)) - x_top_left
            height = float(box.findtext('ymax', 0)) - y_top_left

            self.append(
                file_id,
                class_label,
                x_top_left,
                y_top_left,
                width,
                height,
                truncated=truncated,
                occluded=occluded,
                difficult=difficult
            )
