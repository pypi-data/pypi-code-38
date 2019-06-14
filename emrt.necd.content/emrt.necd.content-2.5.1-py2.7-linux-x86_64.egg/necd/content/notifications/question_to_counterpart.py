from Acquisition import aq_parent
from emrt.necd.content.constants import ROLE_CP
from emrt.necd.content.constants import ROLE_LR
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import notify


def notification_cp(context, event=None, reassign=False):
    """
    To:     CounterParts
    When:   New draft question to comment on
    """
    _temp = PageTemplateFile('question_to_counterpart.pt')

    should_run = (
        event
        and event.action in ['request-for-counterpart-comments']
        or reassign
    )

    if should_run:
        observation = aq_parent(context)
        subject = u'New draft question to comment'
        notify(
            observation,
            _temp,
            subject,
            role=ROLE_CP,
            notification_name='question_to_counterpart'
        )


def notification_lr(context, event):
    """
    To:     LeadReviewer
    When:   New draft question to comment on
    """
    _temp = PageTemplateFile('question_to_counterpart.pt')

    if event.action in ['request-for-counterpart-comments']:
        observation = aq_parent(context)
        subject = u'New draft question to comment'
        notify(
            observation,
            _temp,
            subject,
            role=ROLE_LR,
            notification_name='question_to_counterpart'
        )
