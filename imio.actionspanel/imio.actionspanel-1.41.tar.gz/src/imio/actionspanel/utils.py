# -*- coding: utf-8 -*-

from imio.actionspanel import ActionsPanelMessageFactory as _
from plone import api
from Products.CMFCore.permissions import View


def unrestrictedRemoveGivenObject(object_to_delete):
    """
      This method removes a given object but as a Manager,
      so calling it will have relevant permissions.
      This is done to workaround a strange Zope behaviour where to remove an object,
      the user must have the 'Delete objects' permission on the parent which is not always easy
      to handle.  This is called by the 'remove_givenuid' view that does the checks if user
      has at least the 'Delete objects' permission on the p_object_to_delete.
    """
    # removes the object
    parent = object_to_delete.aq_inner.aq_parent
    with api.env.adopt_roles(['Manager']):
        parent.manage_delObjects(object_to_delete.getId())


def findViewableURL(context,
                    request,
                    member=None):
    """ """
    if not member:
        member = api.user.get_current()

    redirectToUrl = request.get('HTTP_REFERER')

    if not member.has_permission(View, context):
        # add a specific portal_message before redirecting the user
        msg = _('redirected_after_action_not_viewable',
                default='You have been redirect here because the action you '
                        'just made have made thelement no more viewable to you.')
        plone_utils = api.portal.get_tool('plone_utils')
        plone_utils.addPortalMessage(msg, 'warning')

        http_referer = request['HTTP_REFERER']
        if not http_referer.startswith(context.absolute_url()):
            # HTTP_REFERER is not the object we have not access to anymore
            # we can redirect to it...  probably...
            redirectToUrl = http_referer
        else:
            # if HTTP_REFERER is the object we can not access anymore
            # we will try to find a parent object we can be redirected to
            parent = context.aq_inner.aq_parent
            while (not member.has_permission('View', parent) and
                   not parent.meta_type == 'Plone Site'):
                parent = parent.getParentNode()
            redirectToUrl = parent.absolute_url()
    return redirectToUrl
