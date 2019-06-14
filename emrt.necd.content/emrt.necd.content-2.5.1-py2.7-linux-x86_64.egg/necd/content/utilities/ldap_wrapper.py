from emrt.necd.content.constants import LDAP_BASE
from emrt.necd.content.constants import LDAP_BASE_PROJECTION


def ldap_projection(ldap_const):
    return ldap_const.format(base_dn=LDAP_BASE_PROJECTION)


def ldap_inventory(ldap_const):
    return ldap_const.format(base_dn=LDAP_BASE)


class GetLDAPWrapper(object):

    def __call__(self, context):
        if context.type == 'projection':
            return ldap_projection
        else:
            return ldap_inventory