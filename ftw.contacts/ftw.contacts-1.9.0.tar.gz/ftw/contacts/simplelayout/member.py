from ftw.contacts.interfaces import IMemberAccessor
from ftw.contacts.utils import safe_html
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


class MemberView(BrowserView):
    """View to display a member
    """
    def __init__(self, context, request):
        super(MemberView, self).__init__(context, request)
        self.contact = self.get_related_contact()

    def memberaccessor(self):
        if not self.contact:
            return None
        return IMemberAccessor(self.context)

    @property
    def has_permission(self):
        mtool = getToolByName(self.context, "portal_membership")
        return bool(
            mtool.checkPermission("Modify portal content", self.context))

    def get_related_contact(self):
        if self.context.contact:
            return self.context.contact.to_object
        return None

    @property
    def has_related_contact(self):
        return bool(self.contact)

    def safe_html(self, text):
        return safe_html(text)

    @property
    def function(self):
        # The function of the member block has precedes the function of the contact.
        if self.context.function:
            return self.context.function
        if self.context.acquire_address and self.contact:
            return self.contact.function
        return ''
