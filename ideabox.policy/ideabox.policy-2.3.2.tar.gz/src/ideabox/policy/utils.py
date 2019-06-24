# -*- coding: utf-8 -*-

from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from datetime import datetime
from ideabox.policy import vocabularies
from plone import api
from zope.i18n import translate


def token_type_recovery(value):
    value = value.decode("utf8")
    vocabulary = vocabularies.ThemeVocabulary(None)
    return [
        e.token for e in vocabulary.by_value.values() if translate(e.title) == value
    ][0]


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """

    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


def execute_under_admin(portal, function, *args, **kwargs):
    """ Execude code under admin privileges """
    sm = getSecurityManager()
    try:
        try:
            tmp_user = UnrestrictedUser("admin", "", [""], "")
            # Wrap the user in the acquisition context of the portal
            tmp_user = tmp_user.__of__(portal.acl_users)
            newSecurityManager(None, tmp_user)
            # Call the function
            return function(*args, **kwargs)
        except:
            # If special exception handlers are needed, run them here
            raise
    finally:
        # Restore the old security manager
        setSecurityManager(sm)


def review_state(context):
    return api.content.get_state(obj=context)


def can_view_rating(context):
    _rating_states = ("vote", "result_analysis", "rejected")
    return review_state(context) in _rating_states


def now():
    return datetime.now()
