from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import notify
from emrt.necd.content.constants import ROLE_MSA
from emrt.necd.content.constants import ROLE_SE


def notification_ms(context, event):
    """
    To:     MSAuthority
    When:   Observation was finalised
    """
    _temp = PageTemplateFile('observation_finalised.pt')
    if event.action in ['confirm-finishing-observation']:
        observation = context
        subject = u'An observation for your country was finalised'
        notify(
            observation,
            _temp,
            subject,
            ROLE_MSA,
            'observation_finalised'
        )


def notification_se(context, event):
    """
    To:     SectorExpert
    When:   Observation finalised
    """
    _temp = PageTemplateFile('observation_finalised_rev_msg.pt')
    if event.action in ['confirm-finishing-observation']:
        observation = context
        subject = u'Your observation was finalised'
        notify(
            observation,
            _temp,
            subject,
            ROLE_SE,
            'observation_finalised'
        )
