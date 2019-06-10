# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.viewlet.interfaces
import zope.viewlet.manager
import z3c.pagelet.browser


class IViewletPageManager(zope.viewlet.interfaces.IViewletManager):
    pass


ViewletPageManager = zope.viewlet.manager.ViewletManager(
    "viewletpage", IViewletPageManager)


class ViewletPage(z3c.pagelet.browser.BrowserPagelet):

    template = None

    def __init__(self, context, request):
        super(ViewletPage, self).__init__(context, request)
        self.vm = ViewletPageManager(context, request, self)
        self.vm.template = self.template

    def update(self):
        self.vm.update()

    def render(self):
        return self.vm.render()
