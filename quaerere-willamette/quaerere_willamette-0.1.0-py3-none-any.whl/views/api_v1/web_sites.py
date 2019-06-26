__all__ = ['WebSiteView']

from quaerere_base_flask.views.base import BaseView

from willamette.app_util import get_db
from willamette.models import WebSiteModel
from willamette_common.schemas import WebSiteSchema


class WebSiteView(BaseView):
    def __init__(self):
        WebSiteSchema.model_class = WebSiteModel
        super().__init__(WebSiteModel, WebSiteSchema, get_db)
