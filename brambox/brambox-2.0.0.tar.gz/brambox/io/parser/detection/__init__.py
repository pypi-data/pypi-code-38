"""
Brambox detection parsers module |br|
These parsers can be used to parse and generate detection files.
"""
from ._base import DetectionParser

from ._coco import *
from ._dollar import *
from ._erti import *
from ._pascalvoc import *
from ._pickle import *
from ._yaml import *

__all__ = ['DetectionParser', 'detection_formats']
detection_formats = {
    'coco': CocoParser,
    'dollar': DollarParser,
    'erti': ErtiParser,
    'pascalvoc': PascalVocParser,
    'pickle': PickleParser,
    'yaml': YamlParser
}
