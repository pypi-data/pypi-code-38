""" 
 * view.common.uiobj.Style.py
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""
from peek_server.ui_main.login import AppLoginElement
from twisted.web._flatten import flattenString
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET

from txhttputil import ElementRenderedCallback


class LoginResource(Resource):
  isLeaf = True

  def render_GET(self, request):
    return self._renderLogin(request)

  def render_POST(self, request):
    return self._renderLogin(request, failed=True)

  def _renderLogin(self, request, failed=False):
    request.responseHeaders.setRawHeaders("authorization", ["basic"])

    callback = ElementRenderedCallback(request).elementRenderedCallback

    request.write('<!DOCTYPE html>\n')

    d = flattenString(request, AppLoginElement(failed=failed))
    d.addBoth(callback)
    return NOT_DONE_YET

class LoginSucceededResource(Resource):
  isLeaf = True

  def render_GET(self, request):
    return self._render(request)

  def render_POST(self, request):
    return self._render(request)

  def _render(self, request):
    request.redirect(request.uri)
    request.finish()
    return NOT_DONE_YET
