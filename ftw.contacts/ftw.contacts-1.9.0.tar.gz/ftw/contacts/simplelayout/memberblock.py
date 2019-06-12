from ftw.contacts.simplelayout.member import MemberView
from ftw.contacts.utils import get_contact_title
from ftw.simplelayout.browser.blocks.base import BaseBlock
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class MemberBlockView(BaseBlock, MemberView):

    template = ViewPageTemplateFile('templates/memberblock.pt')

    def __call__(self):
        # Partial views are encoded wrong when not called by ajax in plone 5.
        # In consequece in tests, encoding errors can appear if we do not
        # disable the diazo theme 'encoder'.
        # Also see: https://github.com/4teamwork/ftw.testbrowser/commit/8ea19ffbefd251cd6712775336d2a1e76beb79de
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return super(MemberBlockView, self).__call__()

    @property
    def image_caption(self):
        mtool = getToolByName(self, "portal_membership")

        if mtool.checkPermission('View', self.context.contact.to_object):
            return self.contact_title
        return ''

    @property
    def contact_title(self):
        return get_contact_title(
            self.context.contact.to_object, display='natural')
