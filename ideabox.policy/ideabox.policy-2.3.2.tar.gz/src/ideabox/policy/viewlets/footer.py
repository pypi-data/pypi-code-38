# -*- coding: utf-8 -*-

from plone import api
from plone.app.layout.viewlets.common import FooterViewlet


class FooterViewlet(FooterViewlet):
    """
    """

    def is_gdpr(self):
        return api.portal.get_registry_record(
            "imio.gdpr.interfaces.IGDPRSettings.is_text_ready", default=False
        )
