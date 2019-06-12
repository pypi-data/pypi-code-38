from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import notify
from emrt.necd.content.constants import ROLE_MSA
from emrt.necd.content.constants import ROLE_SE


MAIL_SUBJECT = u'A {state} observation was recalled'
MAIL_TEMPLATE = 'observation_recalled_{state}_{suffix}.pt'


OBS_STATES = {
    'closed': 'closed',
    'conclusions-lr-denied': 'denied'
}


NOTIFICATION_NAME = 'observation_recalled'
SKIP_UNLESS_ACTION = 'recall-lr'


def factory(role, suffix, for_states):
    def handler(observation, event):
        if event.action != SKIP_UNLESS_ACTION:
            return

        # get previous state
        _wf_state = observation.workflow_history.get(
            'esd-review-workflow')[-2]['review_state']
        _obs_state = OBS_STATES[_wf_state]

        # only handle specific states
        if _obs_state not in for_states:
            return

        _mail_subject = MAIL_SUBJECT.format(state=_obs_state)
        _mail_template = PageTemplateFile(
            MAIL_TEMPLATE.format(state=_obs_state, suffix=suffix)
        )

        notify(
            observation,
            _mail_template,
            _mail_subject,
            role,
            NOTIFICATION_NAME
        )
    return handler


notification_ms = factory(ROLE_MSA, 'msa', for_states=['closed'])
notification_se = factory(ROLE_SE, 'se', for_states=['closed', 'denied'])
