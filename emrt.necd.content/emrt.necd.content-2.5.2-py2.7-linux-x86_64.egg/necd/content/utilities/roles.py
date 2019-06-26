from functools import partial
from itertools import chain
from itertools import product
from itertools import ifilter as filter

from zope.component.hooks import getSite
from zope.component import getUtility

from emrt.necd.content.utilities.interfaces import ILDAPQuery
from emrt.necd.content.utilities.interfaces import IGetLDAPWrapper

from emrt.necd.content.utilities import ldap_utils

from emrt.necd.content.constants import LDAP_SECTOREXP
from emrt.necd.content.constants import LDAP_LEADREVIEW
from emrt.necd.content.constants import LDAP_MSA
from emrt.necd.content.constants import ROLE_MSA
from emrt.necd.content.constants import ROLE_SE
from emrt.necd.content.constants import ROLE_LR


def context_aware_query(context):
    ldap_wrapper = getUtility(IGetLDAPWrapper)(context)
    return ldap_utils.format_or(
        'cn', (
            ldap_wrapper(LDAP_MSA) + '-*',
            ldap_wrapper(LDAP_LEADREVIEW) + '-*',
            ldap_wrapper(LDAP_SECTOREXP) + '-sector*-*'
        )
    )


def f_start(pat, s):
    return s.startswith(pat)


def get_ldap_role_filters(context):
    ldap_wrapper = getUtility(IGetLDAPWrapper)(context)

    f_start_msa = partial(f_start, ldap_wrapper(LDAP_MSA))
    f_start_lr = partial(f_start, ldap_wrapper(LDAP_LEADREVIEW))
    f_start_se = partial(f_start, ldap_wrapper(LDAP_SECTOREXP))

    return f_start_msa, f_start_lr, f_start_se


def setup_reviewfolder_roles(folder):
    site = getSite()
    acl = site['acl_users']['ldap-plugin']['acl_users']

    with getUtility(ILDAPQuery)(acl, paged=True) as q_ldap:
        q_groups = q_ldap.query_groups(context_aware_query(folder), ('cn',))


    groups = [r[1]['cn'][0] for r in q_groups]

    f_start_msa, f_start_lr, f_start_se = get_ldap_role_filters(folder)

    grant = chain(
        product([ROLE_MSA], filter(f_start_msa, groups)),
        product([ROLE_LR], filter(f_start_lr, groups)),
        product([ROLE_SE], filter(f_start_se, groups)),
    )

    for role, g_name in grant:
        folder.manage_setLocalRoles(g_name, [role])

    return folder


class SetupReviewFolderRoles(object):
    def __call__(self, folder):
        return setup_reviewfolder_roles(folder)
