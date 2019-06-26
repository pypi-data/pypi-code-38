__all__ = ['WebPageView']

from quaerere_base_flask.views.base import BaseView

from willamette.app_util import get_db
from willamette.models import WebPageModel
from willamette_common.schemas import WebPageSchema


class WebPageView(BaseView):
    def __init__(self):
        WebPageSchema.model_class = WebPageModel
        super().__init__(WebPageModel, WebPageSchema, get_db)
