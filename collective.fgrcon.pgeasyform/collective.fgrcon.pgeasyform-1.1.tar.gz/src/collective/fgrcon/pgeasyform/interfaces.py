# -*- coding: utf-8 -*-
from collective.easyform import easyformMessageFactory as _
from collective.easyform.actions import IAction
from plone.z3cform.interfaces import IFormWrapper
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import zope.interface
import zope.schema.interfaces


class IPostgresFormWrapper(IFormWrapper):
    pass


class IPostgresExtraData(Interface):
    dt = zope.schema.TextLine(
        title=_(u'Posting Date/Time'),
        required=False,
        default=u'',
        missing_value=u'',
    )
    HTTP_X_FORWARDED_FOR = zope.schema.TextLine(
        title=_(
            u'extra_header',
            default=u'${name} Header',
            mapping={u'name': u'HTTP_X_FORWARDED_FOR'},
        ),
        required=False,
        default=u'',
        missing_value=u'',
    )
    REMOTE_ADDR = zope.schema.TextLine(
        title=_(
            u'extra_header',
            default=u'${name} Header',
            mapping={u'name': u'REMOTE_ADDR'},
        ),
        required=False,
        default=u'',
        missing_value=u'',
    )
    HTTP_USER_AGENT = zope.schema.TextLine(
        title=_(
            u'extra_header',
            default=u'${name} Header',
            mapping={u'name': u'HTTP_USER_AGENT'},
        ),
        required=False,
        default=u'',
        missing_value=u'',
    )


class IPostgresData(IAction):

    """A form action adapter that will save form input data in postgresql table """

    postgres_con = zope.schema.TextLine(
        title=_(
            u'Postgres Connection String',
            default=u"Individual Default Postgres Connection String",
        ),
        description=_(
            u'<br> Database connection string <br>'
            ' dbname="xxx" user="xxx",host= "xxx" password = "xxx"',
            default=u'<br> Database connection string <br>'
            ' dbname="xxx" user="xxx",host= "xxx" password = "xxx"',
        ),
        default=u'',
        missing_value=u'',
        required=True,
    )
    postgres_table_name = zope.schema.TextLine(
        title=_(u'label_postgres_table_name', default=u"Postgres Table Name"),
        description=_(u'....', default=u'....'),
        default=u'',
        missing_value=u'',
        required=True,
    )
    decimal_separator = zope.schema.Bool(
        title=_(
            u'decimal separator',
            default=u'Treat comma also as decimal separator for Float',
        ),
        default=False,
        required=True,
    )

    ExtraData = zope.schema.List(
        title=_(u'label_savedataextra_text', default='Extra Data'),
        description=_(
            u'help_savedataextra_text',
            default=u'Pick any extra data you\'d like saved with the form '
            u'input.',
        ),
        unique=True,
        value_type=zope.schema.Choice(vocabulary='easyform.ExtraDataDL'),
    )


# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""


class ICollectiveFgrconPgeasyformLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
