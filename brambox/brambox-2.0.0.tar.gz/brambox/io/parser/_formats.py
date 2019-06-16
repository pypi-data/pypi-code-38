#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
import logging
from ._base import Parser
from .annotation import *
from .detection import *
from .box import *

__all__ = ['formats', 'register_parser']
log = logging.getLogger(__name__)


formats = {**box_formats}
for key in annotation_formats:
    formats['anno_'+key] = annotation_formats[key]
for key in detection_formats:
    formats['det_'+key] = detection_formats[key]


def register_parser(name, parser):
    """ Registers a parser class so that any function that works with brambox parsers,
    can use this parser as well.

    Args:
        name (str): Key for the parser in the different dictionaries
        parser (brambox.io.parser.Parser): Parser class to register

    Note:
        If your parser is of the type :class:`~brambox.io.parser.annotation.AnnotationParser`,
        it will be registered in :ref:`annotation_formats <brambox.io.parser.annotation_formats>` with `name` as the key
        and under :ref:`formats <brambox.io.formats>` with `'anno_'+name` as the key. |br|
        If it is of the type :class:`~brambox.io.parser.detection.DetectionParser`,
        it will be registered in :ref:`detection_formats <brambox.io.parser.detection_formats>` with `name` as the key
        and under :ref:`formats <brambox.io.formats>` with `'det_'+name` as the key. |br|
        Finally, if it is neither one of those, but just of type :class:`~brambox.io.parser.Parser`,
        it will be registered in both :ref:`box_formats <brambox.io.parser.box_formats>` and :ref:`formats <brambox.io.formats>`
        with `name` as the key. |br|

    Warning:
        You cannot register a parser if that name is already taken!
    """
    if not issubclass(parser, Parser):
        raise TypeError(f'{parser.__name__} is not of type {Parser}')

    if issubclass(parser, AnnotationParser):
        if name in annotation_formats:
            raise KeyError(f'{name} already registered as annotation parser')
        annotation_formats[name] = parser
        formats['anno_'+name] = parser
    elif issubclass(parser, DetectionParser):
        if name in detection_formats:
            raise KeyError(f'{name} already registered as detection parser')
        detection_formats[name] = parser
        formats['det_'+name] = parser
    else:
        if name in formats:
            raise KeyError(f'{name} already registered as box parser')
        box_formats[name] = parser
        formats[name] = parser
