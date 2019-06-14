from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import notify
from emrt.necd.content.constants import ROLE_SE


def notification_se(context, event):
    """
    To:     SectorExpert
    When:   Observation finalisation denied
    """
    _temp = PageTemplateFile('observation_finalisation_denied.pt')

    if event.action in ['deny-finishing-observation']:
        observation = context
        subject = u'Observation finalisation denied'
        notify(
            observation,
            _temp,
            subject,
            ROLE_SE,
            'observation_finalisation_denied'
        )
