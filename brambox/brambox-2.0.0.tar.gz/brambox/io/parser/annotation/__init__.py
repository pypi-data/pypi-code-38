"""
Brambox annotation parsers module |br|
These parsers can be used to parse and generate annotation files.
"""
from ._base import AnnotationParser

from ._coco import *
from ._cvc import *
from ._darknet import *
from ._dollar import *
from ._kitti import *
from ._pascalvoc import *
from ._pickle import *
from ._vatic import *
from ._yaml import *

__all__ = ['AnnotationParser', 'annotation_formats']
annotation_formats = {
    'coco': CocoParser,
    'cvc': CvcParser,
    'darknet': DarknetParser,
    'dollar': DollarParser,
    'kitti': KittiParser,
    'pascalvoc': PascalVocParser,
    'pickle': PickleParser,
    'vatic': VaticParser,
    'yaml': YamlParser
}
