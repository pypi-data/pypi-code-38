import logging

from attune.core.orm.AuditLog import AuditLogger
from attune.txhttputil.auth.UserAccess import UserAccess
from twisted.cred.error import LoginFailed
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_plugin_base.storage.DbConnection import DbSessionCreator

__author__ = 'synerty'

logger = logging.getLogger(__name__)

import ldap


class LdapNotEnabledError(Exception):
    pass


class LdapAuth:

    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def loginLdapUser(self, userName, secret):
        """ Login User

        :param userName: The username of the user.
        :param secret: The users secret password.
        :rtype C{UserAccess}
        """
        (adminLdapGroup, dashLdapGroup, jobLdapGroup,
         ldapDoamin, ldapOuFolders, ldapCnFolders, ldapUri) = self._loadLdapSettings()

        try:

            conn = ldap.initialize(ldapUri)
            conn.protocol_version = 3
            conn.set_option(ldap.OPT_REFERRALS, 0)

            # make the connection
            conn.simple_bind_s('%s@%s' % (userName, ldapDoamin), secret)
            ldapFilter = "(&(objectCategory=person)(objectClass=user)(sAMAccountName=%s))" % userName

            dcParts = ','.join(['DC=%s' % part for part in ldapDoamin.split('.')])

            ldapBases = self._makeLdapBase(ldapOuFolders, userName, "OU")
            ldapBases += self._makeLdapBase(ldapCnFolders, userName, "CN")

            for ldapBase in ldapBases:
                ldapBase = "%s,%s" % (ldapBase, dcParts)

                try:
                    # Example Base : 'CN=atuser1,CN=Users,DC=synad,DC=synerty,DC=com'
                    userDetails = conn.search_st(ldapBase, ldap.SCOPE_SUBTREE, ldapFilter,
                                                 None, 0, 10)

                    if userDetails:
                        break

                except ldap.NO_SUCH_OBJECT:
                    raise

        except ldap.NO_SUCH_OBJECT:
            logger.error("Login failed for %s, failed to query LDAP for user groups",
                         userName)
            AuditLogger.logUser(
                userOrHttpSession=userName,
                action="Login failed, failed to query LDAP for user groups"
            )
            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs")

        except ldap.INVALID_CREDENTIALS:
            logger.error("Login failed for %s, invalid credentials", userName)
            AuditLogger.logUser(userOrHttpSession=userName,
                                action="login attempt failed")
            raise LoginFailed("Username or password is incorrect")

        if not userDetails:
            logger.error("Login failed for %s, failed to query LDAP for user groups",
                         userName)
            AuditLogger.logUser(
                userOrHttpSession=userName,
                action="Login failed, failed to query LDAP for user groups"
            )
            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs")

        userDetails = userDetails[0][1]

        adminLdapGroupSet = set(['CN=%s,%s,%s' % (adminLdapGroup, base, dcParts)
                                 for base in ldapBases])
        jobLdapGroupSet = set(['CN=%s,%s,%s' % (jobLdapGroup, base, dcParts)
                               for base in ldapBases])
        dashLdapGroupSet = set(['CN=%s,%s,%s' % (dashLdapGroup, base, dcParts)
                                for base in ldapBases])

        memberOfSet = set(userDetails['memberOf'])

        isAdminUser = bool(memberOfSet & adminLdapGroupSet)
        isJobUser = bool(memberOfSet & jobLdapGroupSet)
        isDashboardUser = bool(memberOfSet & dashLdapGroupSet)

        print(memberOfSet)
        print(adminLdapGroupSet)
        print(jobLdapGroupSet)
        print(dashLdapGroupSet)

        if not (isAdminUser or isJobUser or isDashboardUser):
            raise LoginFailed("The user is does not belong to any Attune groups")

        userAccess = UserAccess()
        userAccess.username = userName
        userAccess.loggedIn = True
        userAccess.isAdminUser = isAdminUser
        userAccess.isJobUser = isJobUser
        userAccess.isDashboardUser = isDashboardUser

        AuditLogger.logUser(
            userOrHttpSession=userName,
            action="login succeeded",
            data="admin=%s,job=%s,dashboard=%s" % (
                isAdminUser,
                isJobUser,
                isDashboardUser
            )
        )

        return userAccess

    def _loadLdapSettings(self):

        from peek_core_user._private.storage.Setting import ldapSetting, \
            LDAP_ADMIN_GROUP, LDAP_JOB_GROUP, \
            LDAP_DASHBOARD_GROUP, LDAP_DOMAIN_NAME, LDAP_URI, LDAP_CN_FOLDERS, \
            LDAP_OU_FOLDERS

        ormSession = self._dbSessionCreator()
        try:
            ldapSettings = ldapSetting(ormSession)

            adminLdapGroup = ldapSettings[LDAP_ADMIN_GROUP]
            jobLdapGroup = ldapSettings[LDAP_JOB_GROUP]
            dashLdapGroup = ldapSettings[LDAP_DASHBOARD_GROUP]

            ldapDoamin = ldapSettings[LDAP_DOMAIN_NAME]
            ldapCnFolders = ldapSettings[LDAP_CN_FOLDERS]
            ldapOuFolders = ldapSettings[LDAP_OU_FOLDERS]
            ldapUri = ldapSettings[LDAP_URI]

        except Exception as e:
            logger.error("Failed to query for LDAP connection settings")
            logger.exception(e)
            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs")

        finally:
            ormSession.close()

        return (adminLdapGroup, dashLdapGroup, jobLdapGroup, ldapDoamin,
                ldapOuFolders, ldapCnFolders,
                ldapUri)

    def _makeLdapBase(self, ldapFolders, userName, propertyName):
        try:
            ldapBases = []
            for folder in ldapFolders.split(','):
                folder = folder.strip()
                if not folder:
                    continue

                parts = []
                for part in folder.split('/'):
                    part = part.strip()
                    if not part:
                        continue
                    parts.append('%s=%s' % (propertyName, part))

                ldapBases.append(','.join(reversed(parts)))

            return ldapBases

        except Exception as e:
            logger.error(
                "Login failed for %s, failed to parse LDAP %s Folders setting" % propertyName,
                userName)

            logger.exception(e)

            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs")
