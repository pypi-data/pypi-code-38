__all__ = ['WebSiteModel']

import logging

from arango_orm import Collection
from willamette_common.models import WebSiteBase

LOGGER = logging.getLogger(__name__)


class WebSiteModel(Collection, WebSiteBase):
    __collection__ = 'WebSites'
    _index = [{'type': 'hash',
               'fields': ['url', 'inLanguage'],
               'unique': True}]
