from ftw.slider import _
from ftw.slider.interfaces import IContainer
from plone.dexterity.content import Container
from plone.directives.form import Schema
from zope import schema
from zope.interface import implements
import json


def validate_slick_config(value):
    try:
        json.loads(value)
    except ValueError:
        return False

    return True


class IContainerSchema(Schema):
    slick_config = schema.Text(
        title=_(u'slick_config_label', default=u'Configuration'),
        description=_(u'slick_config_description',
                      default=u'See http://kenwheeler.github.io/slick/'),
        required=False,
        default=u'''
            {"autoplay": true,
             "autoplaySpeed": 5000,
             "fade": true,
             "speed": 1500,
             "infinite": true}
        ''',
        constraint=validate_slick_config,
    )


class Topic(Container):
    implements(IContainer)
