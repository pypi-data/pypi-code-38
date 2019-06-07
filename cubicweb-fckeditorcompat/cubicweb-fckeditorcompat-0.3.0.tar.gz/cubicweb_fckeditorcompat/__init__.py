"""cubicweb-fckeditorcompat application package

contains fckeditor 1:2.6.6-3 code
"""

from logilab.common.decorators import monkeypatch

from cubicweb.web.webconfig import WebConfiguration


@monkeypatch(WebConfiguration)
def fckeditor_installed(self):
    if self.uiprops is None:
        return False
    return True


@monkeypatch(WebConfiguration)
def cwproperty_definitions(self):
    for key, pdef in super(WebConfiguration, self).cwproperty_definitions():
        yield key, pdef
