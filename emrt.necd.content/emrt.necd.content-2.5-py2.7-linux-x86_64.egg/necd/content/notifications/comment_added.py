from functools import partial
from itertools import chain
from Products.Five.browser.pagetemplatefile import PageTemplateFile
import plone.api as api

from emrt.necd.content.observation import IObservation
from emrt.necd.content.notifications import utils
from emrt.necd.content.utils import find_parent_with_interface
from emrt.necd.content.constants import ROLE_MSA
from emrt.necd.content.constants import ROLE_MSE
from emrt.necd.content.constants import ROLE_SE
from emrt.necd.content.constants import ROLE_LR
from emrt.necd.content.constants import ROLE_CP


def user_has_role_in_context(role, context):
    user = api.user.get_current()
    roles = user.getRolesInContext(context)
    return role in roles


def notify_role(rolename, tpl_name, notification_name, subject, context):
    template = PageTemplateFile(tpl_name)
    utils.notify(context, template, subject, rolename, notification_name)


def run_rolecheck(context, func):
    """ Runs the `func` checker in the given `context`.
        `func` is a `user_has_role_in_context` partial.
        (e.g. run_rolecheck(observation, USER_IS_SE))
    """
    return func(context)


PARENT_OBSERVATION = partial(find_parent_with_interface, IObservation)
USER_IS_MSE = partial(user_has_role_in_context, ROLE_MSE)
USER_IS_SE = partial(user_has_role_in_context, ROLE_SE)
USER_IS_CP = partial(user_has_role_in_context, ROLE_CP)
USER_IS_LR = partial(user_has_role_in_context, ROLE_LR)


NOTIFY_MSE = partial(
    notify_role, ROLE_MSE, 'comment_to_mse.pt', 'comment_to_mse')

NOTIFY_MSA = partial(
    notify_role, ROLE_MSA, 'comment_to_msa.pt', 'comment_to_msa')


def notification_mse(comment, event):
    """
    To:     MSExperts
    When:   New comment from MSExpert for your country
    """
    observation = PARENT_OBSERVATION(comment)
    if not USER_IS_MSE(observation):
        return

    NOTIFY_MSE(u'New comment from MS Expert', observation)


def notification_msa(comment, event):
    """
    To:     MSAuthority
    When:   New comment from MSExpert for your country
    """
    observation = PARENT_OBSERVATION(comment)
    if not USER_IS_MSE(observation):
        return

    NOTIFY_MSA(u'New comment from MS Expert', observation)


def notify_users(comment, event):
    """
    To:     SectorExpert / CounterPart / LeadReviewer
    When:   New comment

    This is a single function because a user might have multiple roles
    (e.g. CounterPart and SectorExpert, resulting in duplicate emails.
    """

    TEMPLATE = 'new_comment.pt'
    SUBJECT = u'New comment'
    ROLES = (ROLE_CP, ROLE_SE, ROLE_LR)
    CURRENT_USER = api.user.get_current()

    observation = PARENT_OBSERVATION(comment)
    checker = partial(run_rolecheck, observation)

    has_valid_roles = map(checker, (USER_IS_SE, USER_IS_CP, USER_IS_LR))
    if not any(has_valid_roles):
        return

    get_obs_users = partial(utils.get_users_in_context, observation)
    get_users = lambda role: get_obs_users(role, 'new_comment')
    not_current = lambda user: user != CURRENT_USER

    users = tuple(filter(not_current, set(chain(*map(get_users, ROLES)))))

    template = PageTemplateFile(TEMPLATE)
    content = template(**dict(observation=observation))

    utils.send_mail(SUBJECT, utils.safe_unicode(content), users)
