from Acquisition import aq_parent
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import notify
from emrt.necd.content.constants import ROLE_SE


def notification_se(context, event):
    """
    To:     SectorExpert
    When:   Redraft requested by LR.
    """
    _temp = PageTemplateFile('question_redraft.pt')

    if event.action in ['redraft']:
        observation = aq_parent(context)
        subject = u'Redraft requested.'
        notify(
            observation,
            _temp,
            subject,
            ROLE_SE,
            'question_redraft'
        )
