__all__ = ['get_collections', 'WebPageModel', 'WebSiteModel']

import sys, inspect

from arango_orm import Collection

from .web_pages import WebPageModel
from .web_sites import WebSiteModel


def _model_classes():
    for cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if issubclass(cls[1], Collection) and cls[0] != 'Collection':
            yield cls[1]


def get_collections():
    for model in _model_classes():
        yield model
