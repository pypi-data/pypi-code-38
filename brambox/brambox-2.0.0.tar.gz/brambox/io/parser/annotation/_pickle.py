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
class PickleAnnotation:
    def __setstate__(self, state):
        self.data = {}
        self.data['class_label'] = state['class_label']
        self.data['x_top_left'] = state['x_top_left']
        self.data['y_top_left'] = state['y_top_left']
        self.data['width'] = state['width']
        self.data['height'] = state['height']
        self.data['id'] = state['object_id']
        self.data['lost'] = state['lost']
        self.data['difficult'] = state['difficult']

        if 'occluded_fraction' in state:
            self.data['occluded'] = state['occluded_fraction']
        elif 'occlusion_fraction' in state:
            self.data['occluded'] = state['occlusion_fraction']
        elif 'occluded' in state:
            self.data['occluded'] = float(state['occluded'])
        else:
            self.data['occluded'] = 0

        if 'truncated_fraction' in state:
            self.data['truncated'] = state['truncated_fraction']
        else:
            self.data['truncated'] = 0

        if 'ignore' in state:
            self.data['ignore'] = state['ignore']
        else:
            self.data['ignore'] = False
"""
mod = imp.new_module('brambox.boxes.annotations.pickle')
exec(script, mod.__dict__)
sys.modules['brambox.boxes.annotations.pickle'] = mod


class PickleParser(AnnotationParser):
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

        for img, annos in objects.items():
            self.append_image(img)
            for a in annos:
                self.append(img, **a.data)


# Why did you read it ?
