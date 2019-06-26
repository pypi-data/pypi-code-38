from Acquisition import aq_parent
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import notify
from emrt.necd.content.constants import ROLE_MSA
from emrt.necd.content.constants import ROLE_SE


def notification_ms(context, event):
    """
    To:     MSAuthority
    When:   New question for your country
    """
    _temp = PageTemplateFile('question_to_ms.pt')
    if event.action in ['approve-question']:
        observation = aq_parent(context)
        subject = u'New question for your country'
        notify(
            observation,
            _temp,
            subject,
            role=ROLE_MSA,
            notification_name='question_to_ms'
        )


def notification_se(context, event):
    """
    To:     SectorExpert
    When:   Your question was sent to MS
    """
    _temp = PageTemplateFile('question_to_ms_rev_msg.pt')
    if event.action in ['approve-question']:
        observation = aq_parent(context)
        subject = u'Your observation was sent to MS'
        notify(
            observation,
            _temp,
            subject,
            role=ROLE_SE,
            notification_name='question_to_ms'
        )
