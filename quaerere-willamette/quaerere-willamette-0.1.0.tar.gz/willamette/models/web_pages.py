__all__ = ['WebPageModel']
import logging


from arango_orm import Collection
from arango_orm.references import relationship
from willamette_common.models import WebPageBase

from .web_sites import WebSiteModel

LOGGER = logging.getLogger(__name__)


class WebPageModel(Collection, WebPageBase):
    __collection__ = 'WebPages'
    _index = [{'type': 'hash', 'fields': ['url'], 'unique': True}]

    web_site = relationship(WebSiteModel, 'web_site_key')
