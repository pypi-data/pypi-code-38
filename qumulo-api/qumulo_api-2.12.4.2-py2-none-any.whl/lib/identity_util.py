# Copyright (c) 2019 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import re
import sys

import qumulo.lib.obj

# Well known identifiers used internally by QSFS
ADMIN_USER_ID   = u'500'
ADMINS_GROUP_ID = u'512'
USERS_GROUP_ID  = u'513'
GUEST_USER_ID   = u'501'
GUESTS_GROUP_ID = u'514'
EVERYONE_ID = unicode(0x200000000)
CREATOR_GROUP_ID = unicode(0xffffffff00000001)
CREATOR_OWNER_ID = unicode(0xffffffff00000000)
OWNER_RIGHTS_ID = unicode(0xffffffff00000004)
FILE_OWNER_ID = unicode(0xfffffffe00000001)
FILE_GROUP_OWNER_ID = unicode(0xfffffffe00000002)

#   ____                              _
#  / ___|___  _ ____   _____ _ __ ___(_) ___  _ __  ___
# | |   / _ \| '_ \ \ / / _ \ '__/ __| |/ _ \| '_ \/ __|
# | |__| (_) | | | \ V /  __/ |  \__ \ | (_) | | | \__ \
#  \____\___/|_| |_|\_/ \___|_|  |___/_|\___/|_| |_|___/
#  FIGLET: Conversions
#

POSIX_USER_SID_PREFIX  = 'S-1-5-88-1'  # Used as S-1-5-88-1-uid
POSIX_GROUP_SID_PREFIX = 'S-1-5-88-2'  # Used as S-1-5-88-2-gid

def sid_from_posix_uid(uid):
    '''
    Produce the sid that qsfs uses to represent a given NFS uid.
    '''
    return '{}-{}'.format(POSIX_USER_SID_PREFIX, uid)

def sid_from_posix_gid(gid):
    '''
    Produce the sid that qsfs uses to represent a given NFS gid.
    '''
    return '{}-{}'.format(POSIX_GROUP_SID_PREFIX, gid)

def auth_id_from_posix_uid(uid):
    '''
    Produce the auth_id that qsfs uses internally to represent a given NFS uid.
    '''
    return str((3 << 32) + uid)

def auth_id_from_posix_gid(gid):
    '''
    Produces the auth_id that qsfs uses internally to represent a given NFS gid.
    '''
    return str((4 << 32) + gid)

#  ___    _            _   _ _
# |_ _|__| | ___ _ __ | |_(_) |_ _   _
#  | |/ _` |/ _ \ '_ \| __| | __| | | |
#  | | (_| |  __/ | | | |_| | |_| |_| |
# |___\__,_|\___|_| |_|\__|_|\__|\__, |
#                                |___/
#  FIGLET: Identity
#

# A SID starts with S, followed by hyphen separated version, authority, and at
# least one sub-authority
SID_REGEXP = re.compile(r'S-[0-9]+-[0-9]+(?:-[0-9]+)+$')

EVERYONE_NAME = 'Everyone'
GUEST_NAME = 'Guest'

LOCAL_DOMAIN = 'LOCAL'
WORLD_DOMAIN = 'WORLD'
POSIX_USER_DOMAIN = 'POSIX_USER'
POSIX_GROUP_DOMAIN = 'POSIX_GROUP'
AD_DOMAIN = 'ACTIVE_DIRECTORY'
CREATOR_DOMAIN = 'API_CREATOR_DOMAIN'
INTERNAL_DOMAIN = 'API_INTERNAL_DOMAIN'
NULL_DOMAIN = 'API_NULL_DOMAIN'

VALID_DOMAIN_PREFIXES = ('local', 'world', 'ldap_user', 'ldap_group', 'ad')
VALID_IDENTITY_PREFIXES = VALID_DOMAIN_PREFIXES + \
    ('name', 'sid', 'uid', 'gid', 'auth_id')

class Identity(qumulo.lib.obj.Object):
    '''
    Convenience for interacting with APIs which use @ref api_identity.
    '''
    def __init__(self, id_spec):
        '''
        Parse a dict or string representation of an Identity.

        As a string, an Identity can be represented via SID, UID, GID, or QSFS
        auth_id using a type prefix, e.g.:

            sid:S-1-5-88-1
            uid:1001
            gid:2001
            auth_id:12884901889

        Alternatively, a name can be specified. Note that the name might be
        ambiguous (e.g. same name exists in multiple identity sources, like QSFS
        and AD).

        To reduce the likelihood of ambiguity when specifying a name, use a
        domain prefix to declare the identity source, e.g.:

            local:alice
            world:Everyone
            ldap_user:bob
            ldap_group:researchers
            ad:MYDOMAIN\Marketing

        Domain prefixes are optional.
        '''
        if isinstance(id_spec, dict):
            super(Identity, self).__init__(d=id_spec)
            return

        # Attempt to split by type or domain prefix (e.g. uid:, local:)
        identity = [i.strip() for i in id_spec.split(':')]
        if len(identity) > 2:
            raise ValueError("Identity may not have more than one ':'")
        if len(identity) == 1:
            # If prefix-less, assume identity is a name or SID
            identity_capitalized = identity[0].capitalize()
            if SID_REGEXP.match(identity_capitalized):
                attrs = {'sid': identity_capitalized}
            else:
                attrs = {'name': identity[0]}

            super(Identity, self).__init__(d=attrs)
            return

        prefix, identity = identity
        prefix = prefix.lower()
        if prefix in ('uid', 'gid'):
            attrs = {prefix: int(identity)}
        elif prefix == 'auth_id':
            # NB: validate int, and allow hex if desired:
            attrs = {prefix: str(int(identity, base=0))}
        elif prefix in ('sid', 'name'):
            attrs = {prefix: identity}
        elif prefix == 'world':
            if identity.lower() != EVERYONE_NAME.lower():
                raise ValueError('Identity prefix "world" may only be used '
                    'with the Everyone identity (i.e. world:Everyone)')

            attrs = { 'domain': WORLD_DOMAIN, 'name': EVERYONE_NAME }
        elif prefix == 'local':
            attrs = { 'domain': LOCAL_DOMAIN, 'name': identity }
        elif prefix == 'ldap_user':
            attrs = { 'domain': POSIX_USER_DOMAIN, 'name': identity }
        elif prefix == 'ldap_group':
            attrs = { 'domain': POSIX_GROUP_DOMAIN, 'name': identity }
        elif prefix == 'ad':
            attrs = { 'domain': AD_DOMAIN, 'name': identity }
        else:
            raise ValueError('Identity prefix must be ' +
                ', '.join(['"%s"' % v for v in VALID_IDENTITY_PREFIXES[:-1]]) +
                ', or "%s"' % VALID_IDENTITY_PREFIXES[-1])

        super(Identity, self).__init__(d=attrs)

    def __eq__(self, other):
        '''
        Two identities are considered equal if they share at least one common
        attribute.

        N.B. This assumes that names are unique across identity sources, which
        is not guaranteed, but should be very uncommon (see @ref api_identity).

        It is also assumed that @ref self and @ref other are constructed either
        from an API response or string representation of an identity.
        '''
        common = set(other.dictionary().keys())
        common = common.intersection(self.dictionary().keys())
        if 'domain' in common:
            # Unlike the other attributes, domain being equal doesn't imply
            # all other attributes must be equal. If, however, domain is not
            # equal, then the IDs are different (even if, for example, they
            # have the same unqualified name attributes.)
            if self['domain'] != other['domain']:
                return False
            common.discard('domain')
        comp = [other[k] == self[k] for k in common]
        res = all(comp) and (len(comp) > 0)
        assert all(c == res for c in comp)
        return res

    def __str__(self):
        '''
        @return A string representation of the Identity, optimized for
        legibility.
        The returned representation can be parsed into an equivalent Identity.
        '''
        return unicode(self).encode(sys.stdout.encoding or 'utf-8')

    def __unicode__(self):
        attrs = self.dictionary()
        if attrs.get('auth_id') == EVERYONE_ID:
            return unicode(EVERYONE_NAME)
        if attrs.get('auth_id') == GUEST_USER_ID:
            return unicode(GUEST_NAME)
        if attrs.get('name') is not None:
            return attrs['name']
        if attrs.get('uid') is not None:
            return u'uid:{}'.format(attrs['uid'])
        if attrs.get('gid') is not None:
            return u'gid:{}'.format(attrs['gid'])
        if attrs.get('sid') is not None:
            if attrs.get('domain') != LOCAL_DOMAIN:
                return attrs['sid']
        if attrs.get('auth_id') is not None:
            return u'auth_id:{}'.format(attrs['auth_id'])

        # At least one field must be present, so by process of elimination,
        # there must be a SID.
        return attrs['sid']

    def has_name(self):
        attrs = self.dictionary()
        return attrs.get('name') is not None

    def pretty_domain(self):
        # Don't pretty print World because it's only for Everyone
        attrs = self.dictionary()
        if attrs.get('domain') == LOCAL_DOMAIN:
            return 'local'
        if attrs.get('domain') == POSIX_USER_DOMAIN:
            return 'ldap_user'
        if attrs.get('domain') == POSIX_GROUP_DOMAIN:
            return 'ldap_group'
        if attrs.get('domain') == AD_DOMAIN:
            return 'ad'
        return None
