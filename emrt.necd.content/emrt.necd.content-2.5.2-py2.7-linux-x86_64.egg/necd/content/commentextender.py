"""
    Documentation:
        -   https://github.com/tisto/collective.ploneboard/blob/master/src/collective/ploneboard/browser/commentextender.py
        -   http://plone.293351.n2.nabble.com/GSoC-2014-Collective-Ploneboard-Attachment-issue-tp7571746p7571837.html
"""
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from Acquisition import Implicit
from emrt.necd.content import MessageFactory as _
from emrt.necd.content.constants import P_OBS_REDRAFT_REASON_VIEW
from persistent import Persistent
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.comment import Comment
from plone.namedfile.field import NamedBlobFile
from plone.z3cform.fieldsets import extensible
from Products.CMFCore import permissions
from z3c.form.field import Fields
from z3c.form import interfaces
from zope import interface
from zope import schema
from zope.annotation import factory
from zope.component import adapts
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICommentExtenderFields(Interface):
    attachment = NamedBlobFile(
        title=_(u"Attachment"),
        description=_(u""),
        required=False,
    )

    redraft_message = schema.Text(
        title=_(u'Redraft reason'),
        required=False,
    )

    redraft_date = schema.Datetime(
        title=_(u'Redraft request date'),
        required=False,
    )


class CommentExtenderFields(Implicit, Persistent):
    interface.implements(ICommentExtenderFields)
    adapts(Comment)
    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'attachment')
    attachment = u""

    security.declareProtected(P_OBS_REDRAFT_REASON_VIEW, 'redraft_message')
    redraft_message = u""

InitializeClass(CommentExtenderFields)

CommentExtenderFactory = factory(CommentExtenderFields)


class CommentExtender(extensible.FormExtender):
    adapts(Interface, IDefaultBrowserLayer, CommentForm)

    fields = Fields(ICommentExtenderFields)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    def update(self):
        self.add(ICommentExtenderFields, prefix="")
        self.move('attachment', after='text', prefix="")
        self.form.description = _(u'Handling of confidential files: '
                u'Please zip your file, protect it with a password, upload it to your reply in the EEA review tool '
                u'and send the password per email to the EMRT-NECD Secretariat mailbox. '
                u'Your password will only be shared with the lead reviewer and sector Expert. '
        )
        self.form.fields['redraft_message'].mode = interfaces.HIDDEN_MODE
        self.form.fields['redraft_date'].mode = interfaces.HIDDEN_MODE
