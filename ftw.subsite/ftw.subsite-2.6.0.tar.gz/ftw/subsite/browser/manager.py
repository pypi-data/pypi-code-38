from ftw.subsite.interfaces import ISubsiteColumn
from plone.app.portlets.manager import ColumnPortletManagerRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ColumnSubsiteManagerRenderer(ColumnPortletManagerRenderer):
    """A renderer for the Subsite dashboard on the front-page,
       based on normal portlets
    """
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, ISubsiteColumn)
    template = ViewPageTemplateFile('column.pt')
