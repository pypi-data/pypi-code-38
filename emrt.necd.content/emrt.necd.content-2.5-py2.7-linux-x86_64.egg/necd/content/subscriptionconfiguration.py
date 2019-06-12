from functools import partial
from plone import api
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five import BrowserView
from Acquisition import aq_inner
from Acquisition import aq_parent
from AccessControl import Unauthorized
from plone.memoize.view import memoize
from zope.component import getUtility
from .observation import IObservation
from .observation import ObservationView
from .reviewfolder import IReviewFolder
from emrt.necd.content.subscriptions.interfaces import INotificationUnsubscriptions

import copy

from emrt.necd.content.utilities.interfaces import IGetLDAPWrapper

from emrt.necd.content.utils import user_has_ldap_role
from emrt.necd.content.constants import ROLE_MSA
from emrt.necd.content.constants import ROLE_MSE
from emrt.necd.content.constants import ROLE_SE
from emrt.necd.content.constants import ROLE_CP
from emrt.necd.content.constants import ROLE_LR
from emrt.necd.content.constants import LDAP_SECTOREXP
from emrt.necd.content.constants import LDAP_LEADREVIEW
from emrt.necd.content.constants import LDAP_MSA
from emrt.necd.content.constants import LDAP_MSEXPERT


LDAP_TO_LOCAL = {
    ROLE_SE: partial(user_has_ldap_role, LDAP_SECTOREXP),
    ROLE_LR: partial(user_has_ldap_role, LDAP_LEADREVIEW),
    ROLE_MSA: partial(user_has_ldap_role, LDAP_MSA),
    ROLE_MSE: partial(user_has_ldap_role, LDAP_MSEXPERT),
}


ROLE_TRANSLATOR = {
    ROLE_SE: 'Sector Expert',
    ROLE_LR: 'Lead Reviewer',
    ROLE_CP: 'Counter Part',
    ROLE_MSA:'Member State Coordinator',
    ROLE_MSE:'Member State Expert',
}


NOTIFICATIONS_PER_ROLE = {
    ROLE_SE: {
        'observation_finalisation_denied': True,
        'observation_finalised': True,
        'observation_recalled': True,
        'question_answered': True,
        'question_redraft': True,
        'question_to_ms': True,
        'new_comment': True,
    },
    ROLE_LR: {
        'conclusion_to_comment': True,
        'observation_finalisation_request': True,
        'question_answered': True,
        'question_ready_for_approval': True,
        'question_to_counterpart': True,
        'new_comment': True,
    },
    ROLE_MSA: {
        'answer_acknowledged': True,
        'observation_finalised': True,
        'observation_recalled': True,
        'question_to_ms': True,
        'comment_to_msa': True,
    },
    ROLE_CP: {
        'conclusion_to_comment': True,
        'question_to_counterpart': True,
        'new_comment': True,
    },
    ROLE_MSE: {
        'answer_to_msexperts': True,
        'question_answered': True,
        'comment_to_mse': True,
    },
}

NOTIFICATION_NAMES = {
    ROLE_SE: {
        'observation_finalisation_denied': 'Observation finalisation denied by LR',
        'observation_finalised': 'Observation finalised by LR',
        'observation_recalled': 'Observation recalled by LR',
        'question_answered': 'Question answered by MS',
        'question_redraft': 'Question redraft requested by LR',
        'question_to_ms': 'Question sent to MS by LR',
        'new_comment': 'New comment is added',
    },
    ROLE_LR: {
        'conclusion_to_comment': 'Conclusion to comment by you as LR',
        'observation_finalisation_request': 'Observation finalisation ready for your approval as LR',
        'question_answered': 'Question answered by MS',
        'question_ready_for_approval': 'Question ready for your approval as LR',
        'question_to_counterpart': 'Question to comment by you as LR',
        'new_comment': 'New comment is added',
    },
    ROLE_MSA: {
        'answer_acknowledged': 'Answer acknowledged by sector expert',
        'observation_finalised': 'Observation finalised by LR',
        'observation_recalled': 'Observation recalled by LR',
        'question_to_ms': 'Question to be answered by your country',
        'comment_to_msa': 'New comment from MS Expert',
    },
    ROLE_CP: {
        'conclusion_to_comment': 'Conclusion to comment by you as counterpart',
        'question_to_counterpart': 'Question to comment by you as counterpart',
        'new_comment': 'New comment is added',
    },
    ROLE_MSE: {
        'answer_to_msexperts': 'New question to comment by you as MS expert',
        'question_answered': 'Question answered by MS',
        'comment_to_mse': 'New comment from MS Expert',
    }
}


class SubscriptionConfigurationMixin(BrowserView):

    @memoize
    def user(self):
        if api.user.is_anonymous():
            raise Unauthorized
        return api.user.get_current()

    def user_roles(self, context=None, translated_roles=True):
        if context is None:
            context = self.context

        user = self.user()
        roles = []
        for role in self._user_roles(context, user):
            if translated_roles:
                translated = ROLE_TRANSLATOR.get(role)
                if translated is not None:
                    roles.append(translated)
            else:
                if role in ROLE_TRANSLATOR.keys():
                    roles.append(role)
        return roles

    def get_unsubscribed_notifications(self, context=None):
        if context is None:
            context = self.context

        if not(
                IReviewFolder.providedBy(context)
                or IObservation.providedBy(context)
            ):
            return {}

        user = self.user()
        adapted = INotificationUnsubscriptions(context)
        data = adapted.get_user_data(user.getId())

        if IReviewFolder.providedBy(context):
            return data

        if not data:
            parent = aq_parent(aq_inner(context))
            return self.get_unsubscribed_notifications(context=parent)

        return data


    def my_subscriptions(self):
        roles = []

        roles = self.user_roles(translated_roles=False)

        unsubscribed_notifications = self.get_unsubscribed_notifications()

        items = {}
        for role in roles:
            data = copy.copy(NOTIFICATIONS_PER_ROLE.get(role))
            for unsubscribed in unsubscribed_notifications.get(role, []):
                data[unsubscribed] = False

            items[role] = data
        return items

    def notification_name(self, rolename, notification_name):
        return NOTIFICATION_NAMES.get(rolename, {}).get(
            notification_name, notification_name
        )

    def translate_rolename(self, rolename):
        return ROLE_TRANSLATOR.get(rolename, rolename)


class SubscriptionConfigurationReview(SubscriptionConfigurationMixin):
    def _user_roles(self, context, user):
        groups = user.getGroups()
        ldap_wrapper = getUtility(IGetLDAPWrapper)(context)
        return tuple(
            role for role, checker in LDAP_TO_LOCAL.items()
            if checker(groups=groups, ldap_wrapper=ldap_wrapper)
        )


class SubscriptionConfiguration(SubscriptionConfigurationMixin, ObservationView):

    def _user_roles(self, context, user):
        return api.user.get_roles(user=user, obj=context)

    def has_local_notifications_settings(self):
        user = api.user.get_current()
        adapted = INotificationUnsubscriptions(self.context)
        data = adapted.get_user_data(user.getId())

        return data and True or False


class SaveSubscriptionsMixin(BrowserView):

    def render(self):
        user_roles = []
        if self.request.get('REQUEST_METHOD') == 'POST':
            user = self.user()
            data = self.request.get('subscription_data')
            adapted = INotificationUnsubscriptions(self.context)
            user_roles = self.user_roles(translated_roles=False)
            to_delete = {}
            for item in data:
                copied_item = dict(item)
                rolename = copied_item.get('name')
                del copied_item['name']
                if rolename in user_roles:
                    notifications = set(NOTIFICATIONS_PER_ROLE.get(rolename))
                    deleted = notifications.difference(set(copied_item.keys()))
                    to_delete[rolename] = deleted

            adapted.unsubscribe(user.getId(), notifications=to_delete)
            status = IStatusMessage(self.request)
            status.add('Subscription preferences saved correctly', type='info')
            url = self.context.absolute_url()
            return self.request.response.redirect(url)

        status = IStatusMessage(self.request)
        status.add('There was an error', type='error')
        return self.request.response.redirect(self.context.absolute_url())


class SaveSubscriptionsReview(
        SubscriptionConfigurationReview, SaveSubscriptionsMixin):
    """ Save class for Review folder """


class SaveSubscriptions(SubscriptionConfiguration, SaveSubscriptionsMixin):
    """ Save class for Observation """


class ClearSubscriptions(SubscriptionConfigurationMixin):
    def render(self):
        user = self.user()
        adapted = INotificationUnsubscriptions(self.context)
        adapted.unsubscribe(user.getId())

        status = IStatusMessage(self.request)
        status.add('Local subscription preferences cleared', type='info')
        return self.request.response.redirect(self.context.absolute_url())
