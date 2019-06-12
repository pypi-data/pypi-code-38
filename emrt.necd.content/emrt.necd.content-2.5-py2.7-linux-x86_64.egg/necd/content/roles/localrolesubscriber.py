from Acquisition import aq_inner
from Acquisition import aq_parent

from zope.component import getUtility

import plone.api as api

from emrt.necd.content.utilities.interfaces import IGetLDAPWrapper
from emrt.necd.content.reviewfolder import IReviewFolder

from emrt.necd.content.constants import LDAP_SECTOREXP
from emrt.necd.content.constants import LDAP_LEADREVIEW
from emrt.necd.content.constants import LDAP_MSA
from emrt.necd.content.constants import ROLE_MSA
from emrt.necd.content.constants import ROLE_SE
from emrt.necd.content.constants import ROLE_LR


def grant_local_roles(context):
    """ add local roles to the groups when adding an observation
    """
    country = context.country.lower()
    sector = context.ghg_source_category_value()
    applies_to = [context]
    parent = aq_parent(aq_inner(context))
    if IReviewFolder.providedBy(parent):
        applies_to.append(parent)

    context.__ac_local_roles_block__ = True

    ldap_wrapper = getUtility(IGetLDAPWrapper)(context)

    for obj in applies_to:
        _roles_start = obj.get_local_roles()

        api.group.grant_roles(
            groupname='{}-{}-{}'.format(
                ldap_wrapper(LDAP_SECTOREXP), sector, country),
            roles=[ROLE_SE],
            obj=obj,
        )
        api.group.grant_roles(
            groupname='{}-{}'.format(ldap_wrapper(LDAP_LEADREVIEW), country),
            roles=[ROLE_LR],
            obj=obj,
        )
        api.group.grant_roles(
            groupname='{}-{}'.format(ldap_wrapper(LDAP_MSA), country),
            roles=[ROLE_MSA],
            obj=obj,
        )

        _roles_end = obj.get_local_roles()
        # Reindex only if roles were changed.
        if _roles_end != _roles_start:
            obj.reindexObjectSecurity()
