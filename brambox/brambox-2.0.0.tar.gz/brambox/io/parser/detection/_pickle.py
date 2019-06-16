#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   DONT READ THIS FILE
#   It contains really ugly and hacky code... #MaintainBackwardCompabilityOnFiles
#
"""
pickle
------
"""
import logging
import sys
import imp
import pickle
from ._base import *

__all__ = ["PickleParser"]
log = logging.getLogger(__name__)


script = """
class Detection:
    def __setstate__(self, state):
        self.data = {}
        self.data['class_label'] = state['class_label']
        self.data['x_top_left'] = state['x_top_left']
        self.data['y_top_left'] = state['y_top_left']
        self.data['width'] = state['width']
        self.data['height'] = state['height']
        self.data['id'] = state['object_id']
        self.data['confidence'] = state['confidence']
"""
mod = imp.new_module('brambox.boxes.detections.detection')
exec(script, mod.__dict__)
sys.modules['brambox.boxes.detections.detection'] = mod


class PickleParser(DetectionParser):
    """
    Warning:
        This parser is deprecated and should only be used to deserialize data saved with the brambox v1 pickle parser.
    """
    parser_type = ParserType.SINGLE_FILE
    extension = '.pkl'
    read_mode = 'rb'

    def __init__(self, **kwargs):
        super().__init__()
        log.deprecated('This parser is deprecated and can only deserialize existing files! Please use the PandasParser if you want pickle/binary files')

    def serialize(self, df):
        raise NotImplementedError('This parser is deprecated and can only deserialize existing files! Please use the PandasParser if you want pickle/binary files')

    def deserialize(self, bytestream, file_id=None):
        objects = pickle.loads(bytestream)

        for img, dets in objects.items():
            self.append_image(img)
            for d in dets:
                self.append(img, **d.data)


# Why did you read it ?
