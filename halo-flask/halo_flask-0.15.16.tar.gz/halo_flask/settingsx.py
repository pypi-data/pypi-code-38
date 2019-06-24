from __future__ import print_function

from flask import current_app as app
from halo_flask.classes import AbsBaseClass

class settingsx(AbsBaseClass):
    def __getattribute__(self, name):
        global flx
        try:
            settings = app.config
            attr = settings.get(name)
            return attr
        except RuntimeError as e:
            print("settingsx=" + name + " error:" + str(e))
            return None
