from Acquisition import aq_inner, aq_parent
from DateTime import DateTime
from ftw.subsite import _
from plone.app.portlets.portlets import base
from plone.app.uuid.utils import uuidToObject
from plone.app.z3cform.wysiwyg.widget import WysiwygFieldWidget
from plone.formwidget.contenttree import ContentTreeFieldWidget
from plone.formwidget.contenttree import UUIDSourceBinder
from plone.namedfile.field import NamedImage
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import form, button, field
from z3c.form.interfaces import INPUT_MODE
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import implements


class ITeaserPortlet(IPortletDataProvider):
    """A portlet which can some given Infos
    """

    teasertitle = schema.TextLine(title=_(u'Title'),
                                  description=u'',
                                  required=True)

    teaserdesc = schema.Text(title=_(u'Description'),
                             description=u'',
                             required=True)

    internal_target = schema.Choice(title=_(u"Internal Target"),
                                    description=_(u"Find an internal target \
 for this image to link to"),
                                   required=False,
                                   source=UUIDSourceBinder({})
                                    )
    image = NamedImage(title=_(u'Image'),
                        description=u'',
                        required=True)

    imagetitle = schema.TextLine(
        title=_(
            u'label_imagetitle',
            default=u'Image Title',
        ),
        description=_(
            u'help_imagetitle',
            default=u'The provided image title will be used as alt-text.',
        ),
        required=True,
    )


class Assignment(base.Assignment):
    implements(ITeaserPortlet)

    def __init__(self, assignment_context_path=None, teasertitle='',
                 teaserdesc='', image=None, _image=None,
                 imagetitle='', internal_target=None, image_timestamp=None):

        # ftw.publisher support
        if _image:
            image = _image

        self.assignment_context_path = assignment_context_path
        self.teasertitle = teasertitle
        self.teaserdesc = teaserdesc
        self._image = image
        self.imagetitle = imagetitle
        self.internal_target = internal_target
        self.image_timestamp = image_timestamp or DateTime()

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self.image_timestamp = DateTime()
        self._image = image

    @property
    def title(self):
        return self.teasertitle


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('teaserportlet.pt')

    def getTeaserTitle(self):
        return self.data.teasertitle

    def getTeaserDesc(self):
        return self.data.teaserdesc

    @property
    def internal_url(self):
        object_path = self.data.internal_target
        internal_obj = uuidToObject(object_path)
        if internal_obj:
            return internal_obj.absolute_url()
        else:
            return ''

    @property
    def image_tag(self):
        state = getMultiAdapter((self.context, self.request),
                                name="plone_portal_state")
        portal = state.portal()

        assignments = portal.unrestrictedTraverse(
            self.data.assignment_context_path)
        assignment_url = assignments.absolute_url()
        modified = self.data.image_timestamp
        return u"<img src='{0}/{1}/@@image?_={2}' alt='{3}'/>".format(
            assignment_url,
            self.data.__name__,
            modified.millis(),
            getattr(self.data, 'imagetitle', '')
        )


class AddForm(form.AddForm):
    fields = field.Fields(ITeaserPortlet)

    label = _(u"Add Teaser Portlet")
    description = _(u"Shows the given infos on the front-page.")

    def __init__(self, context, request):
        super(AddForm, self).__init__(context, request)
        self._finishedAdd = None
        self.status = None

    def updateWidgets(self):
        self.fields['teaserdesc'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget
        self.fields['internal_target'].widgetFactory = ContentTreeFieldWidget

        super(AddForm, self).updateWidgets()

    def nextURL(self):
        editview = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(editview))
        url = str(getMultiAdapter((context, self.request),
                                  name=u"absolute_url"))
        return url

    @button.buttonAndHandler(_(u"label_save", default=u"Save"), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    @button.buttonAndHandler(_(u"label_cancel", default=u"Cancel"),
                             name='cancel_add')
    def handleCancel(self, action):
        nextURL = self.nextURL()
        self.request.response.redirect(nextURL)

    def add(self, obj):
        ob = self.context.add(obj)
        self._finishedAdd = True
        return ob

    def create(self, data):

        portal_path_l = len(
            self.context.portal_url.getPortalObject().getPhysicalPath())
        assignment_context_path = '/'.join(
            self.context.__parent__.getPhysicalPath()[portal_path_l:])

        return Assignment(
            assignment_context_path=assignment_context_path, **data)


class EditForm(form.EditForm):
    fields = field.Fields(ITeaserPortlet)

    label = _(u"Edit Teaser Portlet")
    description = _(u"Shows the given infos on the front-page.")

    def updateWidgets(self):
        self.fields['teaserdesc'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget
        self.fields['internal_target'].widgetFactory = ContentTreeFieldWidget
        super(EditForm, self).updateWidgets()
