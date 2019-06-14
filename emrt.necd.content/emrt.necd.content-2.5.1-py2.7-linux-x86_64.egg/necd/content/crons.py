import logging
from AccessControl import getSecurityManager
from AccessControl.User import UnrestrictedUser
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from emrt.necd.content.constants import LDAP_TERT


class UpdateLDAPUsersVocabulariesCron(BrowserView):
    """Update ldap user vocabularies
       call it on port
       http://localhost:8080/Plone/cron_update_vocabularies
    """

    @property
    def acl_users(self):
        return getToolByName(self.context, 'acl_users')

    def switchToManager(self):
        """
        assume the security context of a Manager
        """
        old_sm = getSecurityManager()
        tmp_user = UnrestrictedUser('temp_usr', '', ['Manager'], '')
        tmp_user = tmp_user.__of__(self.acl_users)

        newSecurityManager(None, tmp_user)
        return old_sm

    def returnToNormalUser(sm):
        setSecurityManager(sm)

    @property
    def target_vocabularies(self):
        return [LDAP_TERT]

    def get_users(self, groupname):

        group = self.acl_users.getGroupById(groupname)

        users = []

        if group is not None:
            for member_id in group.getMemberIds():
                user = self.acl_users.getUserById(member_id)
                if user is not None:
                    users.append((
                        member_id,
                        user.getProperty('fullname') or member_id
                    ))

        return users

    def __call__(self):
        logger = logging.getLogger("emrt.necd.content - update vocabularies cron: ")
        vtool = getToolByName(self.context, 'portal_vocabularies')
        for groupname in self.target_vocabularies:
            voc = vtool.getVocabularyByName(groupname)
            if not voc:
                logger.warning(
                    "vocabulary %s not found" % groupname
                )
                continue

            users = self.get_users(groupname)
            for userid, fullname in users:
                if userid not in voc:
                    sm = self.switchToManager()
                    voc.invokeFactory(
                        type_name='SimpleVocabularyTerm',
                        id=userid)
                    voc[userid].setTitle(fullname)
                    voc[userid].reindexObject()
                    self.returnToNormalUser()
                    logger.info(
                        "Term (%s, %s) added into %s" % (userid, fullname, groupname)
                    )
        return 'Done'
