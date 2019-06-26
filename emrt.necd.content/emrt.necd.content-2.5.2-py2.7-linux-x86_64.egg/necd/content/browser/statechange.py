import re
from functools import partial
from operator import itemgetter
import Globals
from Acquisition import aq_parent, aq_inner
from emrt.necd.content import MessageFactory as _
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form.form import Form
from zope import schema
from zope.interface import Interface
from zope.component import getUtility
from DateTime import DateTime
from emrt.necd.content.notifications import answer_to_msexperts
from emrt.necd.content.notifications import question_to_counterpart
from emrt.necd.content.reviewfolder import IReviewFolder
from emrt.necd.content.utils import find_parent_with_interface
from emrt.necd.content.utils import principals_with_roles
from emrt.necd.content.utilities.interfaces import IGetLDAPWrapper
from emrt.necd.content.constants import LDAP_LEADREVIEW
from emrt.necd.content.constants import LDAP_SECTOREXP
from emrt.necd.content.constants import LDAP_MSEXPERT
from emrt.necd.content.constants import ROLE_CP
from emrt.necd.content.constants import ROLE_SE
from emrt.necd.content.constants import ROLE_LR
from emrt.necd.content.constants import ROLE_MSE

TEST_USERS = ('_necd', 'necd_', 'sectorrevnecd')

PARENT_REVIEWFOLDER = partial(find_parent_with_interface, IReviewFolder)

RE_EXTRACT_SECTOR_COUNTRY = re.compile(r'(sector\d)?-([a-z]{2})$')

def group_matches_sector_and_country(name, pass_sector, pass_country):
    """ If neither sector nor country is found in the group name,
        validate it as True in order to cover lead groups.
    """
    sector, country = RE_EXTRACT_SECTOR_COUNTRY.search(name).groups()
    result = []
    if sector:
        result.append(sector == pass_sector)
    if country:
        result.append(country == pass_country)

    return all(result) if result else True


def filter_groups_for_context(context, names):
    validate_group = partial(
        group_matches_sector_and_country,
        pass_sector=context.ghg_source_category_value(),
        pass_country=context.country,
    )
    return tuple(filter(validate_group, names))


def revoke_roles(username=None, user=None, obj=None, roles=None, inherit=True):
    """
    plone.api.user.revoke_roles implementation as per
    https://github.com/plone/plone.api/pull/200
    """
    if user is None:
        user = api.user.get(username=username)
    # check we got a user
    if user is None:
        raise api.InvalidParameterError("User could not be found")

    if isinstance(roles, tuple):
        roles = list(roles)

    if 'Anonymous' in roles or 'Authenticated' in roles:
        raise api.InvalidParameterError

    actual_roles = list(api.user.get_roles(user=user, obj=obj, inherit=inherit))
    if actual_roles.count('Anonymous'):
        actual_roles.remove('Anonymous')
    if actual_roles.count('Authenticated'):
        actual_roles.remove('Authenticated')

    roles = list(set(actual_roles) - set(roles))

    if obj is None:
        user.setSecurityProfile(roles=roles)
    elif not roles:
        obj.manage_delLocalRoles([user.getId()])
    else:
        obj.manage_setLocalRoles(user.getId(), roles)


def exclude_test_users(userdata):
    """ Filter out test user ids if not in development mode.
    """
    if Globals.DevelopmentMode:
        return userdata

    userid = itemgetter(0)

    def drop(data):
        return not tuple(
            ex for ex in TEST_USERS
            if ex in userid(data)
        )

    return filter(drop, userdata)


class IFinishObservationReasonForm(Interface):

    comments = schema.Text(
        title=_(u'Enter comments if you want'),
        required=False,
    )


class FinishObservationReasonForm(Form):
    fields = field.Fields(IFinishObservationReasonForm)
    label = _(u'Request finalisation of the observation')
    description = _(u'Check the reason for requesting the closure of this observation')
    ignoreContext = True

    @button.buttonAndHandler(u'Request finalisation of the observation')
    def finish_observation(self, action):
        comments = self.request.get('form.widgets.comments')
        with api.env.adopt_roles(['Manager']):
            self.context.closing_comments = comments
            return self.context.content_status_modify(
                workflow_action='finish-observation',
            )

        self.request.response.redirect(self.context.absolute_url())

    def updateWidgets(self):
        super(FinishObservationReasonForm, self).updateWidgets()
        self.widgets['comments'].rows = 15

    def updateActions(self):
        super(FinishObservationReasonForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')
            self.actions[k].addClass('defaultWFButton')


class IDenyFinishObservationReasonForm(Interface):

    comments = schema.Text(
        title=_(u'Enter your reasons to deny the finishing of this observation'),
        required=False,
    )


class DenyFinishObservationReasonForm(Form):
    fields = field.Fields(IDenyFinishObservationReasonForm)
    label = _(u'Deny finish observation')
    description = _(u'Check the reason for denying the finishing of this observation')
    ignoreContext = True

    @button.buttonAndHandler(u'Deny finishing observation')
    def finish_observation(self, action):
        comments = self.request.get('form.widgets.comments')
        with api.env.adopt_roles(['Manager']):
            if api.content.get_state(self.context) == 'close-requested':
                self.context.closing_deny_comments = comments
                return self.context.content_status_modify(
                    workflow_action='deny-finishing-observation',
                )

        return self.response.redirect(self.context.absolute_url())

    def updateWidgets(self):
        super(DenyFinishObservationReasonForm, self).updateWidgets()
        self.widgets['comments'].rows = 15

    def updateActions(self):
        super(DenyFinishObservationReasonForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


class RecallObservation(BrowserView):
    def __call__(self):
        state = api.content.get_state(self.context)
        if state == 'conclusions-lr-denied':
            self.context.closing_deny_comments = ''

        with api.env.adopt_roles(['Manager']):
            return self.context.content_status_modify(
                workflow_action='recall-lr',
            )

        return self.response.redirect(self.context.absolute_url())


class AssignFormMixin(BrowserView):

    index = None

    _managed_role = None

    _revoke_on_call = None

    _msg_no_usernames = None

    def show_test_users(self):
        user = api.user.get_current()

        return any(usr in user.getUserName() for usr in TEST_USERS) \
               or 'Manager' in user.getRoles()

    def _get_wf_action(self):
        raise NotImplementedError

    def _assignation_target(self):
        raise NotImplementedError

    def _target_groupnames(self):
        raise NotImplementedError

    def _extra_usernames(self, target):
        return []

    def _is_managed_role(self, username):
        return self._managed_role in api.user.get_roles(
            username=username,
            obj=self._assignation_target(),
            inherit=False
        )

    def revoke_all_roles(self):
        with api.env.adopt_roles(['Manager']):
            target = self._assignation_target()
            for userId, username, cp in self.get_counterpart_users(False):
                if cp:
                    revoke_roles(
                        username=userId,
                        obj=target,
                        roles=[self._managed_role],
                        inherit=False,
                    )

    def get_users_from_group(self, group):
        users = group.getGroupMembers()
        return [
            (u.getId(), u.getProperty('fullname', u.getId())) for u in users]

    def get_counterpart_users(self, exclude_test=True):
        users = []

        if self.show_test_users():
            exclude_test = False

        current_user_id = api.user.get_current().getId()

        group_tool = api.portal.get_tool('portal_groups')
        _groups = map(group_tool.getGroupById, self._target_groupnames())
        groups = filter(bool, _groups) # filter out None

        for res in map(self.get_users_from_group, groups):
            matched = [
                (user_id, user_name, self._is_managed_role(user_id)) for
                user_id, user_name in res if
                user_id != current_user_id
            ]
            users.extend(matched)

        result = list(set(users))

        if exclude_test:
            return exclude_test_users(result)
        else:
            return result


    def __call__(self):
        """ Perform the update and redirect if necessary, or render the page
        """
        target = self._assignation_target()
        if self.request.get('send', None):
            usernames = self.request.get('counterparts', None)
            if not usernames:
                status = IStatusMessage(self.request)
                msg = self._msg_no_usernames
                status.addStatusMessage(msg, "error")
                return self.index()

            self.revoke_all_roles()

            usernames.extend(self._extra_usernames(target))
            for username in usernames:
                api.user.grant_roles(
                    username=username,
                    roles=[self._managed_role],
                    obj=target
                )

            target.reindexObjectSecurity()

            wf_action = self._get_wf_action()
            if wf_action:
                return self.context.content_status_modify(
                    workflow_action=wf_action)
            else:
                status = IStatusMessage(self.request)
                msg = _(u'There was an error. Try again please')
                status.addStatusMessage(msg, "error")
                url = self.context.absolute_url()
                return self.request.response.redirect(url)

        else:
            if self._revoke_on_call:
                self.revoke_all_roles()
            return self.index()


class IAssignAnswererForm(Interface):
    answerers = schema.Choice(
        title=_(u'Select the answerers'),
        vocabulary=u'plone.app.vocabularies.Users',
    )

    workflow_action = schema.TextLine(
        title=_(u'Workflow action'),
        required=True
    )


class AssignAnswererForm(AssignFormMixin):

    index = ViewPageTemplateFile('templates/assign_answerer_form.pt')

    _managed_role = ROLE_MSE
    _revoke_on_call = True
    _msg_no_usernames = _(
        u'You need to select at least one expert for discussion')

    def _assignation_target(self):
        return aq_parent(aq_inner(self.context))

    def _extra_usernames(self, target):
        country = target.country
        return ['necd_eea_{}_exp'.format(country)]

    def _target_groupnames(self):
        context = aq_inner(self.context)
        observation = aq_parent(context)
        country = observation.country.lower()
        ldap_wrapper = getUtility(IGetLDAPWrapper)(context)
        return ['{}-{}'.format(ldap_wrapper(LDAP_MSEXPERT), country)]

    def _get_wf_action(self):
        if api.content.get_state(self.context) in [
                u'pending',
                u'recalled-msa',
                u'pending-answer-drafting']:
            return 'assign-answerer'


class ReAssignMSExpertsForm(AssignAnswererForm):
    def __call__(self):

        target = self._assignation_target()
        if self.request.form.get('send', None):
            usernames = self.request.get('counterparts', None)
            if not usernames:
                status = IStatusMessage(self.request)
                msg = _(u'You need to select at least one expert for discussion')
                status.addStatusMessage(msg, "error")
                return self.index()

            self.revoke_all_roles()

            usernames.extend(self._extra_usernames(target))
            for username in usernames:
                api.user.grant_roles(username=username,
                    roles=[self._managed_role],
                    obj=target)
            target.reindexObjectSecurity()

            answer_to_msexperts.notification_mse(self.context, reassign=True)

            return self.request.response.redirect(target.absolute_url())

        else:
            return self.index()


class IAssignCounterPartForm(Interface):
    counterpart = schema.TextLine(
        title=_(u'Select the counterpart'),
    )

    workflow_action = schema.TextLine(
        title=_(u'Workflow action'),
        required=True
    )


class AssignCounterPartForm(AssignFormMixin):

    index = ViewPageTemplateFile('templates/assign_counterpart_form.pt')

    _managed_role = ROLE_CP
    _revoke_on_call = True
    _msg_no_usernames = _(
        u'You need to select at least one counterpart')

    def _assignation_target(self):
        return aq_parent(aq_inner(self.context))

    def _get_wf_action(self):
        if api.content.get_state(self.context) == 'draft':
            return 'request-for-counterpart-comments'

    def _target_groupnames(self):
        reviewfolder = PARENT_REVIEWFOLDER(self.context)
        rolenames = (ROLE_SE, ROLE_LR)
        from_reviewfolder = principals_with_roles(reviewfolder, rolenames)
        validated_groups = filter_groups_for_context(
            self.context, from_reviewfolder)
        ldap_wrapper = getUtility(IGetLDAPWrapper)(self.context)
        static = (ldap_wrapper(LDAP_LEADREVIEW), ldap_wrapper(LDAP_SECTOREXP))
        return static + validated_groups

    def get_current_counterparters(self):
        """ Return list of current counterparters
        """
        target = self._assignation_target()
        local_roles = target.get_local_roles()
        users = [
            u[0] for u in local_roles if self._managed_role in u[1]
        ]

        skipped_extra_users = self._extra_usernames(target)
        return [
            api.user.get(user)
            for user in users
            if user not in skipped_extra_users
        ]


class IAssignConclusionReviewerForm(Interface):
    reviewers = schema.Choice(
        title=_(u'Select the conclusion reviewers'),
        vocabulary=u'plone.app.vocabularies.Users',
    )


class ReAssignCounterPartForm(AssignCounterPartForm):

    index = ViewPageTemplateFile('templates/assign_counterpart_form.pt')

    def __call__(self):
        """Perform the update and redirect if necessary, or render the page
        """
        target = self._assignation_target()
        if self.request.form.get('send', None):
            counterparts = self.request.get('counterparts', None)
            if counterparts is None:
                status = IStatusMessage(self.request)
                msg = self._msg_no_usernames
                status.addStatusMessage(msg, "error")
                return self.index()

            self.revoke_all_roles()

            for username in counterparts:
                api.user.grant_roles(username=username,
                    roles=[self._managed_role],
                    obj=target)
            target.reindexObjectSecurity()

            status = IStatusMessage(self.request)
            msg = _(u'CounterParts reassigned correctly')
            status.addStatusMessage(msg, "info")
            url = self.context.absolute_url()

            question_to_counterpart.notification_cp(
                self.context, reassign=True)

            return self.request.response.redirect(url)

        else:
            return self.index()


class AssignConclusionReviewerForm(AssignFormMixin):

    index = ViewPageTemplateFile('templates/assign_conclusion_reviewer_form.pt')

    _managed_role = ROLE_CP
    _revoke_on_call = False
    _msg_no_usernames = _(
        u'You need to select at least one reviewer for conclusions')

    def update(self):
        self._revoke_all_roles()

    def _assignation_target(self):
        return aq_inner(self.context)

    def _target_groupnames(self):
        reviewfolder = PARENT_REVIEWFOLDER(self.context)
        rolenames = (ROLE_SE, ROLE_LR)
        from_reviewfolder = principals_with_roles(reviewfolder, rolenames)
        validated_groups = filter_groups_for_context(
            self.context, from_reviewfolder)
        ldap_wrapper = getUtility(IGetLDAPWrapper)(self.context)
        static = (ldap_wrapper(LDAP_LEADREVIEW), ldap_wrapper(LDAP_SECTOREXP))
        return static + validated_groups

    def _get_wf_action(self):
        return 'request-comments'

    def updateActions(self):
        super(AssignConclusionReviewerForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


class UpdateWorkflow(BrowserView):
    def __call__(self):
        state_id = self.request.form.get('state_id', None)
        workflow_id = self.request.form.get('workflow_id', None)

        if not (state_id and workflow_id):
            return 'Nothing!'

        wft = self.context.portal_workflow
        workflow = wft.getWorkflowById(workflow_id)
        state_variable = workflow.state_var
        wf_state = {
            'action': None,
            'actor': None,
            'comments': "Setting state to %s" % state_id,
            state_variable: state_id,
            'time': DateTime(),
            }

        wft.setStatusOf(workflow_id, self.context, wf_state)
        workflow.updateRoleMappingsFor(self.context)

        return 'Success!'
