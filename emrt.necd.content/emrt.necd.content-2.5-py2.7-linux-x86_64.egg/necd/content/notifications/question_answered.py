from Acquisition import aq_parent
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import notify
from emrt.necd.content.constants import ROLE_SE
from emrt.necd.content.constants import ROLE_LR
from emrt.necd.content.constants import ROLE_MSE


def notification_lr(context, event):
    """
    To:     LeadReviewer
    When:   New answer from country
    """
    _temp = PageTemplateFile('question_answered_lr_msg.pt')

    if event.action in ['answer-to-lr']:
        observation = aq_parent(context)
        subject = u'New answer from country'
        notify(
            observation,
            _temp,
            subject,
            ROLE_LR,
            'question_answered'
        )


def notification_se(context, event):
    """
    To:     SectorExpert
    When:   New answer from country
    """
    _temp = PageTemplateFile('question_answered_rev_msg.pt')

    if event.action in ['answer-to-lr']:
        observation = aq_parent(context)
        subject = u'New answer from country'
        notify(
            observation,
            _temp,
            subject,
            ROLE_SE,
            'question_answered'
        )


def notification_rev_msexperts(context, event):
    """
    To:     MSExperts
    When:   New answer from country
    """
    _temp = PageTemplateFile('question_answered_msexperts_msg.pt')
    if event.action in ['answer-to-lr']:
        observation = aq_parent(context)
        subject = u'New answer from country'
        notify(
            observation,
            _temp,
            subject,
            ROLE_MSE,
            'question_answered'
        )
