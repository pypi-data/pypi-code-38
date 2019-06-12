from Products.Five.browser import BrowserView
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from zope import schema
from cs.dxfeatured import MessageFactory as _
from zope.interface import implements
from plone.app.textfield import RichText


# Interface class; used to define content-type schema.
class IFeatured(form.Schema, IImageScaleTraversable):
    """
    Featured Element
    """
    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/featured.xml to define the content type
    # and add directives here as necessary.
    image = NamedBlobImage(
            title=_(u"Lead Image"),
            description=u"",
            required=True,
        )

    link = schema.TextLine(
        title=_(u'Link'),
        description=_(u'This link will be for the carousel image link'),
        required=True,
        )

    text = RichText(title=_(u'Featured text'),
        required=False,
        )
try:
    from plone.multilingualbehavior.interfaces import ILanguageIndependentField
    from zope.interface import alsoProvides
    alsoProvides(IFeatured['image'], ILanguageIndependentField)
except:
    pass

# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class Featured(dexterity.Item):
    implements(IFeatured)
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# templates called featuredview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type


class FeaturedView(BrowserView):
    """
    The view
    """