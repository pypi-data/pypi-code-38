import logging
from typing import List

from twisted.cred.error import LoginFailed

from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple

__author__ = 'synerty'

logger = logging.getLogger(__name__)

import ldap

'''
{'objectClass': [b'top', b'person', b'organizationalPerson', b'user'], 'cn': [b'attest'],
 'givenName': [b'attest'],
 'distinguishedName': [b'CN=attest,OU=testou,DC=synad,DC=synerty,DC=com'],
 'instanceType': [b'4'], 'whenCreated': [b'20170505160836.0Z'],
 'whenChanged': [b'20190606130621.0Z'], 'displayName': [b'attest'],
 'uSNCreated': [b'16498'],
 'memberOf': [b'CN=Domain Admins,CN=Users,DC=synad,DC=synerty,DC=com',
              b'CN=Enterprise Admins,CN=Users,DC=synad,DC=synerty,DC=com',
              b'CN=Administrators,CN=Builtin,DC=synad,DC=synerty,DC=com'],
 'uSNChanged': [b'73784'], 'name': [b'attest'],
 'objectGUID': [b'\xee\x1bV\x8dQ\xackE\x82\xd9%_\x18\xadjO'],
 'userAccountControl': [b'66048'], 'badPwdCount': [b'0'], 'codePage': [b'0'],
 'countryCode': [b'0'], 'badPasswordTime': [b'132042996316396717'], 'lastLogoff': [b'0'],
 'lastLogon': [b'132042996806397639'], 'pwdLastSet': [b'132042997225927009'],
 'primaryGroupID': [b'513'], 'objectSid': [
    b'\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00D:3|X\x8f\xc7\x08\xe6\xeaV\xc8Q\x04\x00\x00'],
 'adminCount': [b'1'], 'accountExpires': [b'9223372036854775807'], 'logonCount': [b'36'],
 'sAMAccountName': [b'attest'], 'sAMAccountType': [b'805306368'],
 'userPrincipalName': [b'attest@synad.synerty.com'], 'lockoutTime': [b'0'],
 'objectCategory': [b'CN=Person,CN=Schema,CN=Configuration,DC=synad,DC=synerty,DC=com'],
 'dSCorePropagationData': [b'20190606130621.0Z', b'20190606130016.0Z',
                           b'20170506090346.0Z', b'16010101000000.0Z'],
 'lastLogonTimestamp': [b'132042996806397639']}
'''

class LdapNotEnabledError(Exception):
    pass


class LdapAuth:

    def checkPassBlocking(self, dbSession, userName, password) -> List[str]:
        """ Login User

        :param dbSession:
        :param userName: The username of the user.
        :param password: The users secret password.
        :rtype
        """
        (ldapDoamin, ldapOuFolders, ldapCnFolders, ldapUri) = self._loadLdapSettings(
            dbSession
        )

        try:

            conn = ldap.initialize(ldapUri)
            conn.protocol_version = 3
            conn.set_option(ldap.OPT_REFERRALS, 0)

            # make the connection
            conn.simple_bind_s('%s@%s' % (userName, ldapDoamin), password)
            ldapFilter = "(&(objectCategory=person)(objectClass=user)(sAMAccountName=%s))" % userName

            dcParts = ','.join(['DC=%s' % part for part in ldapDoamin.split('.')])

            ldapBases = self._makeLdapBase(ldapOuFolders, userName, "OU")
            ldapBases += self._makeLdapBase(ldapCnFolders, userName, "CN")

            for ldapBase in ldapBases:
                ldapBase = "%s,%s" % (ldapBase, dcParts)

                try:
                    # Example Base : 'CN=atuser1,CN=Users,DC=synad,DC=synerty,DC=com'
                    userDetails = conn.search_st(ldapBase, ldap.SCOPE_SUBTREE,
                                                 ldapFilter, None, 0, 10)

                    if userDetails:
                        break

                except ldap.NO_SUCH_OBJECT:
                    raise

        except ldap.NO_SUCH_OBJECT:
            logger.error("Login failed for %s, failed to query LDAP for user groups",
                         userName)
            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs")

        except ldap.INVALID_CREDENTIALS:
            logger.error("Login failed for %s, invalid credentials", userName)
            raise LoginFailed("Username or password is incorrect")

        if not userDetails:
            logger.error("Login failed for %s, failed to query LDAP for user groups",
                         userName)
            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs")

        userDetails = userDetails[0][1]

        groups = []
        for memberOf in userDetails['memberOf']:
            group = memberOf.decode().split(',')[0]
            if '=' in group:
                group = group.split('=')[1]
            groups.append(group)

        userTitle = None
        if userDetails['displayName']:
            userTitle = userDetails['displayName'][0].decode()

        email = None
        if userDetails['userPrincipalName']:
            email = userDetails['userPrincipalName'][0].decode()

        userUuid = None
        if userDetails['distinguishedName']:
            userUuid = userDetails['distinguishedName'][0].decode()

        self._makeOrCreateInternalUserBlocking(dbSession,
                                               userName, userTitle, userUuid, email)

        return groups

    def _makeOrCreateInternalUserBlocking(self, dbSession,
                                          userName, userTitle, userUuid, email):

        internalUser = dbSession.query(InternalUserTuple) \
            .filter(InternalUserTuple.userName == userName) \
            .all()

        if internalUser:
            return

        newInternalUser = InternalUserTuple(
            userName=userName,
            userTitle=userTitle,
            userUuid=userUuid,
            email=email
        )

        dbSession.add(newInternalUser)
        dbSession.commit()

    def _loadLdapSettings(self, dbSession):

        from peek_core_user._private.storage.Setting import ldapSetting, \
            LDAP_DOMAIN_NAME, LDAP_URI, LDAP_CN_FOLDERS, \
            LDAP_OU_FOLDERS

        try:
            ldapSettings = ldapSetting(dbSession)

            ldapDoamin = ldapSettings[LDAP_DOMAIN_NAME]
            ldapCnFolders = ldapSettings[LDAP_CN_FOLDERS]
            ldapOuFolders = ldapSettings[LDAP_OU_FOLDERS]
            ldapUri = ldapSettings[LDAP_URI]

        except Exception as e:
            logger.error("Failed to query for LDAP connection settings")
            logger.exception(e)
            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs")

        return ldapDoamin, ldapOuFolders, ldapCnFolders, ldapUri

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
