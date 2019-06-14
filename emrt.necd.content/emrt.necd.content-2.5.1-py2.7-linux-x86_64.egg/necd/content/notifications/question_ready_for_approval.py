from Acquisition import aq_parent
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import notify
from emrt.necd.content.constants import ROLE_LR


def notification_lr(context, event):
    """
    To:     LeadReviewer
    When:   New question for approval
    """
    _temp = PageTemplateFile('question_ready_for_approval.pt')

    if event.action in ['send-to-lr']:
        observation = aq_parent(context)
        subject = u'New question for approval'
        notify(
            observation,
            _temp,
            subject,
            ROLE_LR,
            'question_ready_for_approval'
        )
