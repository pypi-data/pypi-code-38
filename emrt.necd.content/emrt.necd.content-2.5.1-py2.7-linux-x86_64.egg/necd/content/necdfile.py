from AccessControl import getSecurityManager
from Acquisition import aq_parent
from emrt.necd.content import MessageFactory as _
from plone.dexterity.browser import add
from plone.dexterity.content import Item
from plone.directives import form
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from zope import schema
from zope.interface import implementer

# Interface class; used to define content-type schema.
class INECDFile(form.Schema, IImageScaleTraversable):
    """
    Files with special needs
    """
    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    form.primary('file')
    file = NamedBlobFile(
        title=_(u'File'),
        required=True,
    )


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
@implementer(INECDFile)
class NECDFile(Item):
    # Add your class methods and properties here

    def can_edit(self):
        sm = getSecurityManager()
        parent = aq_parent(self)
        edit = False
        if parent.portal_type == 'Comment':
            edit = sm.checkPermission('emrt.necd.content: Edit Comment', self)
        elif parent.portal_type == 'CommentAnswer':
            edit = sm.checkPermission('emrt.necd.content: Edit CommentAnswer', self)
        return edit


class AddForm(add.DefaultAddForm):
    label = 'file'
    description = ''

    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):
        super(AddForm, self).handleAdd(self, action)
        question = self.context.aq_parent
        self.request.response.redirect(question.absolute_url())

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        super(AddForm, self).handleCancel(action)

    def update(self):
        super(AddForm, self).update()
        status = IStatusMessage(self.request)

        msg = _(u'Handling of confidential files: '
                u'Please zip your file, protect it with a password, upload it to your reply in the EEA review tool '
                u'and send the password per email to the EMRT-NECD Secretariat mailbox. '
                u'Your password will only be shared with the lead reviewer and sector Expert. '
        )

        status.add(msg, type='info')

    def updateFields(self):
        super(AddForm, self).updateFields()
        self.fields = field.Fields(INECDFile).omit('title')
        self.groups = [g for g in self.groups if g.label == 'label_schema_default']


class AddView(add.DefaultAddView):
    form = AddForm


class NECDFileView(BrowserView):
    def render(self):
        url = aq_parent(self.context).absolute_url()
        return self.response.redirect(url)
