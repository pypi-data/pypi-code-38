from .utils import Utils
import logging
l = logging.getLogger(__name__)



class AppSettings(Utils):
    myconf = ['adminname','adminpass','customtemplatesrc']
    customtemplatesrc = '/tmp'
