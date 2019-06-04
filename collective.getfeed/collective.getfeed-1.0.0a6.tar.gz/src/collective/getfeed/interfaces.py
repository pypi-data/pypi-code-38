# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from collective.getfeed import _
from plone.namedfile import field
from plone.supermodel import model
from zope import schema
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectivegetfeedCoreLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IFeed(model.Schema):
    """Feed content type interface."""

    url = schema.TextLine(
        title=_(u'URL'),
        description=_(u'The Feed address (url) to this blog.'),
        required=True,
    )


class IFeedItem(model.Schema):
    """Feed Item content type interface."""

    image = field.NamedBlobImage(
        title=_(u'Image'),
        required=False,
    )

    url = schema.TextLine(
        title=_(u'URL'),
        description=_(u'The address of original url.'),
        required=True,
    )
